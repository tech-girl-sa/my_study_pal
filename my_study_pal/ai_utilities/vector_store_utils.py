from typing import Union
from langchain_postgres import PGVector
from django.conf import settings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from my_study_pal.courses.models import Course, Section
from my_study_pal.subjects.models import Subject


def create_vector_store():
    collection_name = "sections"
    connection = settings.PGVECTOR_DB_URL
    #base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    #embeddings = OllamaEmbeddings(model="llama3", base_url=base_url) consumes a lot of memory requires setting up local server
    #embeddings = VertexAIEmbeddings(model="text-embedding-004") requires billing
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    sections = Section.objects.all()
    section_documents = [
        Document(page_content=section.title,
                 metadata={"course_id": section.course.id,
                           "section_id": section.id,
                           "user_id": section.course.subject.user.id})
        for section in sections]
    vector_store.add_documents(section_documents)



class VectorStoreManager():
    connection = settings.PGVECTOR_DB_URL
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    def __init__(self, vector_store_name):
        self.vector_store = PGVector(
        embeddings=self.embeddings,
        collection_name=vector_store_name,
        connection=self.connection,
        use_jsonb=True,
    )

    def add_vector(self, object:Union[Subject, Course, Section]):
        content = object.title
        metadata = self.construct_metadata(object)
        self.vector_store.add_documents([Document(page_content=content, metadata=metadata)])

    def construct_metadata(self, object: Union[Subject, Course, Section]):
        if type(object) == Subject:
            return {"subject_id":object.id, "user_id":object.user.id}
        elif type(object) == Course:
            return {"course_id":object.id ,"subject_id": object.subject.id, "user_id": object.subject.user.id}
        else:
            return {"section_id": object.id, "course_id": object.course.id, "user_id": object.course.subject.user.id}

