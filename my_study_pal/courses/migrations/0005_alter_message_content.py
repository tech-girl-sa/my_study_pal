# Generated by Django 4.2.20 on 2025-05-03 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_message_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(max_length=5000, verbose_name='Content'),
        ),
    ]
