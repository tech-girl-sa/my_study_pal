from django.template.defaultfilters import title
from langchain_community.document_loaders import PyPDFLoader
import urllib.parse
import os
import re
from django.conf import settings
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from llama_parse import LlamaParse
import nltk
from my_study_pal.ai_utilities.ai_agents import AIAgentClientManager
from my_study_pal.ai_utilities.models import Settings
from my_study_pal.courses.models import Course, Section, Chunk
from my_study_pal.documents.models import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from docling.document_converter import DocumentConverter
from langchain_huggingface import HuggingFaceEmbeddings
import math
from my_study_pal.subjects.models import Subject

CLOUDE_KEY = os.environ.get('CLAUDE_API_KEY')


def get_document_full_path(document: Document):
    base_dir = str(settings.BASE_DIR)
    file_relative = "/my_study_pal/documents"
    dir_path = urllib.parse.urljoin(base_dir, file_relative)
    file_path = urllib.parse.urljoin(dir_path, document.file.path)
    return  file_path

def ensure_punkt_downloaded():
    """Download punkt only once, when actually needed."""
    if not hasattr(ensure_punkt_downloaded, "_done"):
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)
        ensure_punkt_downloaded._done = True


class DocumentProcessor:
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2")
    ]
    max_chunk_size = 500

    def __init__(self, document:Document):
        self.document = document

    def load_and_split_document(self):
        lines = self.extract_text_with_font_info()
        text = self.convert_to_markdown(lines)
        docs = self.split_document(text)
        return docs


    def split_document(self,text):
        markdown_splitter = MarkdownHeaderTextSplitter(self.headers_to_split_on)
        splits = markdown_splitter.split_text(text)
        return splits

    def extract_text_with_font_info(self):
        text_elements = [
            text_element
            for page_layout in extract_pages(get_document_full_path(self.document))
            for text_element in page_layout
            if isinstance(text_element, LTTextContainer)
        ]
        font_sizes=[]
        is_multiple = []
        element_lines= [line for text in text_elements for line in text if line.get_text().strip()]
        text_lines = [line.get_text().strip() for line in element_lines]
        for line in element_lines:
            first_size = 0
            multiple_sizes = False
            for char in line:
                if isinstance(char, LTChar):
                    if first_size == 0:
                        first_size = char.size
                    elif char.size != first_size:
                        multiple_sizes = True
            font_sizes.append(round(first_size,1))
            is_multiple.append(multiple_sizes)
        font_size_info = {
            "top_biggest_three": sorted(set(font_sizes),reverse=True)[:3],
            "lines" : list( zip(text_lines, font_sizes, is_multiple)),
        }
        print(font_size_info)
        return font_size_info

    def is_header(self,line):
        header_patterns = [
            r'^\d+(\.\d+)*[\)\.\-: ]+\s*[A-Z].*$',  # Arabic
            r'^[IVXLCDMivxlcdm]+[\)\.\-: ]+\s*[A-Z].*$',  # Roman
            r'^[A-Z][\)\.\-: ]+\s*[A-Z].*$',  # Alpha
            r'^[A-Z]\d+[\)\.\-: ]+\s*[A-Z].*$',  # A1. Title
            r'^[A-Z0-9\s\-:]{5,}$',  # ALL CAPS
            r'^[A-Z][a-z]+.*:\s*$',  # Title with colon
            r'^[A-Za-z]+\s+((\d+([.\-]\d+)*)|([A-Za-z]+)|([IVXLCDMivxlcdm]+))[\.\-:]?\s*.*$', # Word + number letter or roman (Chapter 1, Part 2, Lesson 3)
        ]
        return any(re.match(p, line.strip()) for p in header_patterns)


    def get_title_and_headers(self, pdf_lines):
        title = [line[0] for line in pdf_lines["lines"] if line[1]==pdf_lines["top_biggest_three"][0]][0]
        headers = [line[0] for line in pdf_lines["lines"] if line[1]==pdf_lines["top_biggest_three"][1] and self.is_header(line[0])]
        print(title,headers)
        return title, headers

    def convert_to_markdown(self, pdf_lines):
        title,headers = self.get_title_and_headers(pdf_lines)
        converted_lines = []
        for line in pdf_lines["lines"]:
            if line[0] == title:
                converted_lines.append(f"# {line[0]}")
            elif line[0] in headers:
                converted_lines.append(f"## {line[0]}")
            else:
                converted_lines.append(line[0])
        return "\n".join(converted_lines)


    def process_document(self,ai_agent_token, course_id, user_id):
        #TODO add user to document
        sections = self.load_and_split_document()
        print(self.document)
        title = sections[0].metadata.get("Header 1")
        self.document.title = title
        #course and subject creation TODO subject affiliation will be based on user choice
        extra_data={
            "new_course" : False,
            "course_title" : "",
            "existing_subject_title" : "",
            "new_subject_title" : "",
        }

        if course_id:
            course = Course.objects.filter(id=course_id).first()
        else:
            course = Course.objects.filter(title=self.document.title, subject__user_id=user_id).first()
        manager = AIAgentClientManager(ai_agent_token)
        if not course:
            course = Course(title = title)
            extra_data["new_course"] = True
            suggested_subject = manager.get_course_subject_title(title, user_id)
            if not suggested_subject["existing_subject_id"]:
                subject = Subject(title= suggested_subject["suggested_subject_title"],
                                  description=suggested_subject["suggested_subject_description"],
                                  user_id=user_id)
                subject.save()
                extra_data["new_subject_title"]  = subject.title
                course.subject = subject
            else:
                course.subject = Subject.objects.filter(id=suggested_subject["existing_subject_id"]).first()
                print(suggested_subject["existing_subject_id"], course.id)
                extra_data["existing_subject_title"]  = course.subject.title
            course.save()
        else:
            if course.document:
                #TODO create custom errors handling
                raise Exception("course already have a document.One document is allowed at a time")
        extra_data["course_title"] = course.title
        self.document.course = course
        self.document.save()
        self.save_sections_and_chunks(sections, course)
        return extra_data



    def save_sections_and_chunks(self, sections, course):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        ensure_punkt_downloaded()
        for section in sections:
            section_title = section.metadata.get("Header 2", "Introduction")
            section_instance = Section(title=section_title, course=course)
            section_instance.save()
            section_len = self.get_tokens_number(section.page_content)
            if section_len > self.max_chunk_size:
                chunks_num = math.ceil(section_len / self.max_chunk_size)
                splitter = SemanticChunker(
                    embeddings,
                    number_of_chunks=chunks_num
                )
                chunks = splitter.create_documents([section.page_content])
                for chunk in chunks:
                    chunk_instance = Chunk(content=chunk.page_content, section=section_instance)
                    chunk_instance.save()
            else:
                chunk_instance = Chunk(content=section.page_content, section=section_instance)
                chunk_instance.save()


    def get_tokens_number(self, text):
        text_no_punct = re.sub(r'[^\w\s]', '', text.lower())
        words = nltk.word_tokenize(text_no_punct)
        return len(words)








def docling_extracter(document:Document):
    source = get_document_full_path(document)
    converter = DocumentConverter()
    result = converter.convert(source)
    print(result.document.export_to_markdown())

def to_markdown(document:Document):
    parser = LlamaParse(
        api_key=CLOUDE_KEY,
        result_type="markdown"
    )
    documents = parser.load_data(get_document_full_path(document))
    texts = [doc.text for doc in documents]
    content = "".join(texts)
    return content
