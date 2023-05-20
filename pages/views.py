from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import Course, Lecturer, ExamSchedule
from django.contrib.auth.models import User

        
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing')
        else:
            error_message = 'Invalid username or password. Please try again.'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

#@login_required
def landing(request):
    return render(request, 'landing.html', {'user': request.user})

def calendar(request):
    return render(request, 'calendar.html')



########## COURSES ##########

def courses(request):
    # Fetch all courses from the database
    courses = Course.objects.all()
    lecturers = Lecturer.objects.all()
    # Pass the courses to the template
    context = {'courses': courses, 'lecturers': lecturers}
    return render(request, 'courses.html', context)


def add_course(request):
    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_name = request.POST.get('course_name')
        credit_hours = request.POST.get('credit_hours')
        course_lecturer = request.POST.get('course_lecturer')
        course_level = request.POST.get('course_level')
        course_lab_lecturer = request.POST.get('course_lab_lecturer')
        course_past_lecturers = request.POST.getlist('course_past_lecturers')
        course = Course.objects.create(
            course_code=course_code, 
            course_name=course_name, 
            credit_hours=credit_hours, 
            course_lecturer=Lecturer.objects.get(id=int(course_lecturer)) if course_lecturer else None,
            course_level=course_level, 
            course_lab_lecturer=Lecturer.objects.get(id=int(course_lab_lecturer)) if course_lab_lecturer else None,
        )
        for lecturer_id in course_past_lecturers:
            course.course_past_lecturers.add(Lecturer.objects.get(id=int(lecturer_id)))
        
        course.save()
        return redirect('courses')



########## LECTURERS ##########

def lecturers(request):
    lecturers = Lecturer.objects.all()
    courses = Course.objects.all()
    return render(request, 'lecturers.html', {'lecturers': lecturers, 'courses': courses})

def add_lecturer(request):
    if request.method == 'POST':
        lecturer_name = request.POST.get('lecturer_name')
        lecturer_email = request.POST.get('lecturer_email')
        lecturer_phone = request.POST.get('lecturer_phone')
        lecturer_gender = request.POST.get('lecturer_gender')
        lecturer_type = request.POST.get('lecturer_type')
        lecturer_rating = request.POST.get('lecturer_rating')
        lecturer_past_courses = request.POST.get('lecturer_past_courses')
        lecturer = Lecturer.objects.create(
            lecturer_name=lecturer_name,
            lecturer_email=lecturer_email,
            lecturer_number=lecturer_phone,
            lecturer_gender=lecturer_gender,
            lecturer_type=lecturer_type,
            lecturer_rating=lecturer_rating,

        )
        lecturer.save()
        return redirect('lecturers')


########## Add Lexturer to Course ##########
def add_lecturer_to_course(request, course_id):
    if request.method == 'POST':
        lecturer_id = request.POST.get('lecturer')
        course = Course.objects.get(id=course_id)
        lecturer = Lecturer.objects.get(id=lecturer_id)
        course.course_lecturer = lecturer
        course.save()
        lecturer.lecturer_past_courses.add(course)
        return redirect('esnad')



########## EXAM ##########
def exam_dates(request):
    courses = Course.objects.all()
    exam_dates = ExamSchedule.objects.all()
    exam_dates_json = []
    for exam_date in exam_dates:
        exam_dates_json.append({
            'title': exam_date.course.course_name,
            'start': exam_date.exam_date.strftime('%Y-%m-%d') + 'T' + exam_date.start_time.strftime('%H:%M:%S')
        })
    return render(request, 'exam_dates.html', {'courses': courses, 'exam_dates': exam_dates_json})

def add_exam(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        course = Course.objects.get(id=course)
        exam_schedule = ExamSchedule.objects.create(
            course=course,
            exam_date=start_date,
            start_time=start_time,
        )
        exam_schedule.save()
        return redirect('exam_dates')




@csrf_exempt
def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('event_title')
        start_date = request.POST.get('event_start')
        # Convert start_date to datetime object if necessary
        event = Event.objects.create(title=title, start=start_date)
        return JsonResponse({'event_id': event.id})

@csrf_exempt
def update_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        title = request.POST.get('event_title')
        event = Event.objects.get(id=event_id)
        event.title = title
        event.save()
        return JsonResponse({})

@csrf_exempt
def delete_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = Event.objects.get(id=event_id)
        event.delete()
        return JsonResponse({})
    


def assign_lecturer(request):
    if request.method == 'POST':
        lecturer_id = request.POST.get('lecturer_id')
        course_code = request.POST.get('course_code')
        
        lecturer = Lecturer.objects.get(id=lecturer_id)
        course = Course.objects.get(course_code=course_code)  # Get course by its code

        # Check for time conflicts
        if not Lecturer.objects.filter(courses__time=course.time).exists():
            # No conflicts, assign lecturer to course
            lecturer.courses.add(course)
            lecturer.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Time conflict'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def esnad(request):
    lecturers = Lecturer.objects.all()
    courses = Course.objects.all()
    return render(request, 'esnad.html', {'lecturers': lecturers, 'courses': courses})
