from typing import Union

from django.db.models.signals import post_delete
from django.dispatch import receiver

from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
from my_study_pal.courses.models import Course, Section, Message, Chunk
from my_study_pal.subjects.models import Subject


@receiver(post_delete, sender=Subject)
@receiver(post_delete, sender=Course)
@receiver(post_delete, sender=Section)
@receiver(post_delete, sender=Message)
@receiver(post_delete, sender=Chunk)
def cleanup_embeddings_on_delete(sender, instance: Union[Subject, Course, Section, Chunk, Message], **kwargs):
    store = VectorStoreManager(instance.vector_store_name)
    store.delete_vectors([instance.pk])
