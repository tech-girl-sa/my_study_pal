# Generated by Django 4.2.20 on 2025-05-03 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0005_alter_message_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300, verbose_name='Title')),
                ('path', models.CharField(max_length=300, verbose_name='Path of document')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='document', to='courses.course', verbose_name='course')),
            ],
        ),
    ]
