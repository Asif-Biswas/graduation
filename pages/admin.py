from django.contrib import admin
from .models import Lecturer, Course, SemesterSchedule
# Register your models here.
admin.site.register(Lecturer)
admin.site.register(Course)
admin.site.register(SemesterSchedule)
