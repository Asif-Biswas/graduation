# Generated by Django 4.2.1 on 2023-05-23 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_lecturer_lecturer_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_section',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
