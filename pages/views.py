from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import Course, Lecturer, ExamSchedule, Event
from django.contrib.auth.models import User
import datetime
import math


        
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

def logout_view(request):
    logout(request)
    return redirect('login')

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
            'start': exam_date.exam_date.strftime('%Y-%m-%d') + 'T' + exam_date.start_time.strftime('%H:%M:%S'),
            'url': '/delete-exam/' + str(exam_date.id)
        })
    return render(request, 'exam_dates.html', {'courses': courses, 'exam_dates': exam_dates_json})

def add_exam(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        courses = Course.objects.all()
        exam_dates = []
        exam_hours = []
        # add the days to exam_dates list between start_date and end_date
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        delta = end_date - start_date
        for i in range(delta.days + 1):
            # check if the day is a weekend (friday or saturday)
            if (start_date + datetime.timedelta(days=i)).weekday() not in [4, 5]:
                exam_dates.append(start_date + datetime.timedelta(days=i))

        # add the hours to exam_hours list between start_time and end_time
        start_time = datetime.datetime.strptime(start_time, '%H:%M')
        end_time = datetime.datetime.strptime(end_time, '%H:%M')
        delta = end_time - start_time
        for i in range(delta.seconds // 3600 + 1):
            exam_hours.append(start_time + datetime.timedelta(hours=i))

        courses_len = len(courses)
        exam_dates_len = len(exam_dates)

        exams_gradually = exam_dates_len / courses_len
        
        # Assign exams to courses
        first_exam_date_and_time = exam_dates[0].strftime('%Y-%m-%d') + 'T' + exam_hours[0].strftime('%H:%M:%S')
        exam_assigned_at_with_time = [first_exam_date_and_time]

        exam_assigned_at = [exam_dates[0]]
        add_index = 1 if exams_gradually < 1 else int(exams_gradually)
        add_index_fraction = exams_gradually - add_index
        add_index_fraction_backup = add_index_fraction
        fraction_added = False

        for course in courses[1:]:
            # calculate the next add_index
            add_index_fraction = add_index_fraction + add_index_fraction_backup
            if not fraction_added:
                if add_index_fraction >= 1:
                    add_index = add_index + 1
                    add_index_fraction = add_index_fraction - 1
                    fraction_added = True
            else:
                add_index -= 1
                fraction_added = False


            # check if course is last course in the list
            if course == courses[courses_len - 1]:
                last_index = exam_dates_len - 1
                next_exam_date = exam_dates[last_index]
                exam_assigned_at.append(next_exam_date)
            else:
                last_exam_date = exam_assigned_at[-1]
                last_exam_date_index = exam_dates.index(last_exam_date)
                next_exam_date_index = last_exam_date_index + add_index if last_exam_date_index + add_index < exam_dates_len else 0
                next_exam_date = exam_dates[next_exam_date_index]
                exam_assigned_at.append(next_exam_date)

            next_exam_time = exam_hours[0]
            next_exam_date_and_time = next_exam_date.strftime('%Y-%m-%d') + 'T' + next_exam_time.strftime('%H:%M:%S')
            
            while next_exam_date_and_time in exam_assigned_at_with_time:
                # add 4 hours to next_exam_date_and_time
                next_exam_time = next_exam_time + datetime.timedelta(hours=4)
                next_exam_date_and_time = next_exam_date.strftime('%Y-%m-%d') + 'T' + next_exam_time.strftime('%H:%M:%S')
            exam_assigned_at_with_time.append(next_exam_date_and_time)

            # Assign exams to courses

        #print(exam_assigned_at)
        print(exam_assigned_at_with_time)

        # Assign exams to courses
        for date_time in exam_assigned_at_with_time:
            course = courses[exam_assigned_at_with_time.index(date_time)]
            exam_schedule = ExamSchedule.objects.create(
                course=course,
                exam_date=date_time.split('T')[0],
                start_time=date_time.split('T')[1],
            )
            exam_schedule.save()
            
            



        # course = Course.objects.get(id=course)
        # exam_schedule = ExamSchedule.objects.create(
        #     course=course,
        #     exam_date=start_date,
        #     start_time=start_time,
        # )
        # exam_schedule.save()
        return redirect('exam_dates')


def add_exam_single(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')

        course = Course.objects.get(id=course)
        exam_schedule = ExamSchedule.objects.create(
            course=course,
            exam_date=start_date,
            start_time=start_time,
        )
        exam_schedule.save()
        return redirect('exam_dates')


def delete_exam(request, exam_id):
    exam_schedule = ExamSchedule.objects.get(id=exam_id)
    exam_schedule.delete()
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
