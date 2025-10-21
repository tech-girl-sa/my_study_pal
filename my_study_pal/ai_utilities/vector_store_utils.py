from typing import Union
from langchain_postgres import PGVector
from django.conf import settings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from my_study_pal.courses.models import Course, Section, Chunk, Message
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



class VectorStoreManager:
    connection = settings.PGVECTOR_DB_URL
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    class_mapping = {
        Subject().vector_store_name : Subject,
        Course().vector_store_name : Course,
        Section().vector_store_name: Section,
        Chunk().vector_store_name: Chunk,
        Message().vector_store_name: Message
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

    def add_vector(self, object:Union[Subject, Course, Section, Chunk, Message]):
        if hasattr(object, 'title'):
            content = object.title
        else:
            content = object.content
        self.vector_store.add_documents([Document(page_content=content, metadata=object.metadata)])

    def delete_vectors(self, ids:list[int]):
        filters = {"instance_id": {"$in": ids}}
        documents = self.vector_store.similarity_search(
            query="",
            k=1000,
            filter=filters
        )
        ids = [document.id for document in documents]
        self.vector_store.delete(ids)


    def get_similar_topics(self, query, user_id, k=2):
        documents = self.vector_store.similarity_search(query=query, k=k)
        return self.instance_class.objects.filter(id__in=[document.metadata["instance_id"] for document in documents]
                                                  , user__id=user_id)


    def get_similar_chunks(self, query, document_id, section_id=0, k=5):
        filters = {"document_id": {"$eq": document_id}}
        if section_id:
            filters["section_id"] = {"$eq": section_id}
        documents = self.vector_store.similarity_search(
            query=query, k=k,
            filter= filters
        )
        return self.instance_class.objects.filter(id__in=[document.metadata["instance_id"] for document in documents])


    def get_similar_user_messages(self, query,user, section_id, k=3):
        filters = { "sender": {"$eq": Message.SenderChoices.user}}
        filters["section_id"] = {"$eq": section_id}
        filters["user_id"] = {"$eq": user.id}
        documents = self.vector_store.similarity_search(
            query=query, k=k,
            filter=filters
        )
        return self.instance_class.objects.filter(id__in=[document.metadata["instance_id"] for document in documents])
