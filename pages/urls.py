from django.urls import path
from . import views
from .views import landing,add_event,delete_event,update_event, login_view, exam_dates, esnad
from django.contrib.auth.views import LoginView




urlpatterns = [
    # other URL patterns...
    path('', landing, name='landing'),
    path('landing/', landing, name='landing'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('calendar/', views.calendar, name='calendar'),
    path('add-event/', add_event, name='add_event'),
    path('update-event/', update_event, name='update_event'),
    path('delete-event/', delete_event, name='delete_event'),
    path('exam-dates/', exam_dates, name='exam_dates'),
    path('esnad/', esnad, name='esnad'),
    path('assign-lecturer/', views.assign_lecturer, name='assign_lecturer'),


    # Course URLs
    path('courses/', views.courses, name='courses'),
    path('add-course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>', views.edit_course, name='edit_course'),


    # Lecturer URLs
    path('lecturers/', views.lecturers, name='lecturers'),
    path('add-lecturer/', views.add_lecturer, name='add_lecturer'),
    path('edit-lecturer/<int:lecturer_id>', views.edit_lecturer, name='edit_lecturer'),
    path('lecturer-view', views.lecturer_view, name='lecturer_view'),

    # Add Lecturer to Course
    path('add-lecturer-to-course/<int:course_id>', views.add_lecturer_to_course, name='add_lecturer_to_course'),


    # Exam
    path('add-exam', views.add_exam, name='add_exam'),
    path('add-exam-single', views.add_exam_single, name='add_exam_single'),
    path('delete-exam/<int:exam_id>', views.delete_exam, name='delete_exam'),
    path('confirm-delete-exam/<int:exam_id>', views.confirm_delete_exam, name='confirm_delete_exam'),
    path('edit-exam/<int:exam_id>', views.edit_exam, name='edit_exam'),


    # Profile
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]