# Generated by Django 4.2.20 on 2025-05-03 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ai_utilities', '0003_vectorchunk_vectorstore_alter_aimodel_configuration'),
        ('documents', '0001_initial'),
        ('courses', '0005_alter_message_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='vectorstore',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vector_stores', to='documents.document', verbose_name='Document'),
        ),
        migrations.AddField(
            model_name='vectorstore',
            name='section',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vector_store', to='courses.section', verbose_name='Section'),
        ),
        migrations.AddField(
            model_name='vectorchunk',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='courses.message', verbose_name='Message'),
        ),
        migrations.AddField(
            model_name='vectorchunk',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vector_chunks', to='courses.section', verbose_name='Section'),
        ),
        migrations.AddField(
            model_name='vectorchunk',
            name='vector_store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vector_chunks', to='ai_utilities.vectorstore', verbose_name='Vector Store'),
        ),
    ]
