from typing import Union
from langchain_postgres import PGVector
from django.conf import settings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from my_study_pal.courses.models import Course, Section
from my_study_pal.subjects.models import Subject


def create_vector_store():
    collection_name = "courses"
    connection = settings.PGVECTOR_DB_URL
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    instances = Course.objects.all()
    instances_documents = [
        Document(page_content=instance.title,
                 metadata={"subject_id": instance.subject.id,
                           "instance_id": instance.id,
                           "user_id": instance.subject.user.id})
        for instance in instances]
    vector_store.add_documents(instances_documents)



class VectorStoreManager():
    connection = settings.PGVECTOR_DB_URL
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    class_mapping = {
        Subject().vector_store_name : Subject,
        Course().vector_store_name : Course,
        Section().vector_store_name: Section
    }

    def __init__(self, vector_store_name):
        self.vector_store = PGVector(
        embeddings=self.embeddings,
        collection_name=vector_store_name,
        connection=self.connection,
        use_jsonb=True,
    )
        self.instance_class = self.class_mapping[vector_store_name]
        self.vector_store_name = vector_store_name

    def add_vector(self, object:Union[Subject, Course, Section]):
        content = object.title
        metadata = self.construct_metadata(object)
        self.vector_store.add_documents([Document(page_content=content, metadata=metadata)])

    def construct_metadata(self, object: Union[Subject, Course, Section]):
        metadata_mappings = {
            Subject().vector_store_name: {"instance_id": object.id, "user_id": object.user.id},
            Course().vector_store_name: {"instance_id": object.id, "subject_id": object.subject.id,
                                       "user_id": object.subject.user.id},
            Section().vector_store_name: {"instance_id": object.id, "course_id": object.course.id,
                                        "user_id": object.course.subject.user.id}
        }
        return metadata_mappings[object.vector_store_name]


    def get_similar_topics(self, query, k=2):
        documents = self.vector_store.similarity_search(query=query, k=k)
        return self.instance_class.objects.filter(id__in=[document.metadata["instance_id"] for document in documents])

