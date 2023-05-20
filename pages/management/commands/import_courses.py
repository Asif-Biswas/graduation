import csv
from django.core.management.base import BaseCommand
from pages.models import Course

class Command(BaseCommand):
    help = 'Imports courses from a CSV file to the database'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        with open(csvfile, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header row
            for row in reader:
                course_id, course_name, credit_hours, sections, course_lecturer, course_examdates, course_lab_lecturer, course_material = row
                course = Course.objects.create(
                    course_id=course_id,
                    course_name=course_name,
                    credit_hours=credit_hours,
                    sections=sections,
                    course_lecturer=course_lecturer,
                    course_examdates=course_examdates,
                    course_lab_lecturer=course_lab_lecturer,
                    course_material=course_material
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created course {course}'))
