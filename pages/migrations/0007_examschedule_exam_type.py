# Generated by Django 4.2.1 on 2023-05-23 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_lecturer_lecturer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='examschedule',
            name='exam_type',
            field=models.CharField(default='Final', max_length=20),
        ),
    ]
