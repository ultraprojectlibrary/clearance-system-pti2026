from django.shortcuts import render, redirect
from .models import (
Student,
CustomUser,
Document,
Hod,
Hostel,
Exam_and_record,
Library,
Sport_director,
Student_affair,
Sug,
Statement_Result,
Review,
Department,
Level

)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as log, logout
from django.contrib import messages
from .forms import StudentForm, StudentProfileForm
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404

import os
from django.core.files import File
from PIL import Image
from io import BytesIO
import os
from django.core.files import File
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import *
from .forms import AnnouncementForm


from django.urls import reverse



from .models import Hod, Sug, Sport_director, Library, Hostel, Student_affair, Exam_and_record
from .forms import (
    HodForm, SugForm, SportDirectorForm, LibraryForm,
    HostelForm, StudentAffairForm, ExamAndRecordForm
)





def remove_signature_from_document(doc):
    """
    Function to remove the signature from the document by restoring the original file.
    This assumes the signed document has a prefix 'signed_' and the original document is backed up.
    """
    try:
        # Assuming the signed document has 'signed_' prefix
        original_file_path = doc.file.path.replace("signed_", "")

        # Check if the original document exists
        if os.path.exists(original_file_path):
            with open(original_file_path, "rb") as f:
                # Restore the original file
                doc.file.save(os.path.basename(original_file_path), File(f), save=True)
                return "Signature removed and original document restored."
        else:
            return "Original document not found. Signature not removed."
    except Exception as e:
        return f"Error removing signature: {e}"




def attach_signature(doc, profile):
    base_img_path = doc.file.path
    base_img = Image.open(base_img_path).convert("RGBA")

    signature_path = profile.signature.path
    signature = Image.open(signature_path).convert("RGBA")

    # Resize signature
    max_width = 150
    if signature.width > max_width:
        ratio = max_width / signature.width
        signature = signature.resize((int(signature.width * ratio), int(signature.height * ratio)))

    # Position bottom-right
    base_w, base_h = base_img.size
    sig_w, sig_h = signature.size
    position = (base_w - sig_w - 10, base_h - sig_h - 10)

    # Paste signature
    base_img.paste(signature, position, signature)

    # Save to in-memory buffer
    buffer = BytesIO()
    base_img.convert("RGB").save(buffer, format="JPEG")
    buffer.seek(0)

    # Generate new filename
    original_filename = os.path.basename(base_img_path)
    new_filename = f"signed_{original_filename}"

    # Save as new file object and update model
    doc.file.save(new_filename, File(buffer), save=True)



@login_required(login_url="login")
def dashboard(request):
    if request.user.position == "student":
        profile = Student.objects.get(user = request.user)

        # Get student's documents and clearance status
        documents = Document.objects.filter(student=profile)

        # Get actual staff members for each department with their images
        hod_staff = None
        hod_name = "No HOD Assigned"
        hod_image = None
        try:
            # Get HOD from student's department
            hod_staff = Hod.objects.get(department=profile.department)
            hod_name = hod_staff.user.username
            hod_image = hod_staff.image.url if hod_staff.image else None
        except Hod.DoesNotExist:
            pass

        sug_staff = None
        sug_name = "No Entrepreneurship Officer"
        sug_image = None
        try:
            sug_staff = Sug.objects.first()  # Assuming one Entrepreneurship officer
            if sug_staff:
                sug_name = sug_staff.user.username
                sug_image = sug_staff.image.url if sug_staff.image else None
        except:
            pass

        library_staff = None
        library_name = "No Library Officer"
        library_image = None
        try:
            library_staff = Library.objects.first()
            if library_staff:
                library_name = library_staff.user.username
                library_image = library_staff.image.url if library_staff.image else None
        except:
            pass

        sport_staff = None
        sport_name = "No Sport Director"
        sport_image = None
        try:
            sport_staff = Sport_director.objects.first()
            if sport_staff:
                sport_name = sport_staff.user.username
                sport_image = sport_staff.image.url if sport_staff.image else None
        except:
            pass

        student_affair_staff = None
        student_affair_name = "No Student Affairs Officer"
        student_affair_image = None
        try:
            student_affair_staff = Student_affair.objects.first()
            if student_affair_staff:
                student_affair_name = student_affair_staff.user.username
                student_affair_image = student_affair_staff.image.url if student_affair_staff.image else None
        except:
            pass

        exam_staff = None
        exam_name = "No Exam Officer"
        exam_image = None
        try:
            exam_staff = Exam_and_record.objects.first()
            if exam_staff:
                exam_name = exam_staff.user.username
                exam_image = exam_staff.image.url if exam_staff.image else None
        except:
            pass

        hostel_staff = None
        hostel_name = "No Hostel Officer"
        hostel_image = None
        try:
            hostel_staff = Hostel.objects.first()
            if hostel_staff:
                hostel_name = hostel_staff.user.username
                hostel_image = hostel_staff.image.url if hostel_staff.image else None
        except:
            pass

        # Create clearance status data for each department
        clearance_data = {
            'hod': {
                'name': 'Head of Department',
                'staff_name': hod_name,
                'image': hod_image,
                'default_image': 'images/hod.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'sug': {
                'name': 'Entrepreneurship',
                'staff_name': sug_name,
                'image': sug_image,
                'default_image': 'images/sug.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'library': {
                'name': 'Library Officer',
                'staff_name': library_name,
                'image': library_image,
                'default_image': 'images/library.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'sport_director': {
                'name': 'Sport Director',
                'staff_name': sport_name,
                'image': sport_image,
                'default_image': 'images/sport.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'student_affair': {
                'name': 'Student Affairs',
                'staff_name': student_affair_name,
                'image': student_affair_image,
                'default_image': 'images/student_affairs.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'exam_record': {
                'name': 'Exam & Records',
                'staff_name': exam_name,
                'image': exam_image,
                'default_image': 'images/exam.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            },
            'hostel': {
                'name': 'Hostel Officer',
                'staff_name': hostel_name,
                'image': hostel_image,
                'default_image': 'images/hostel.jpg',
                'status': 'pending',
                'approved': False,
                'documents': [],
                'feedback': []
            }
        }

        # Update clearance data based on actual document approvals
        # First, collect all document statuses for each department
        for doc in documents:
            # HOD
            clearance_data['hod']['documents'].append({
                'title': doc.title,
                'approved': doc.hod_approved,
                'approved_by': doc.hod_approved_by.username if doc.hod_approved_by else None
            })

            # Entrepreneurship
            clearance_data['sug']['documents'].append({
                'title': doc.title,
                'approved': doc.sug_approved,
                'approved_by': doc.sug_approved_by.username if doc.sug_approved_by else None
            })

            # Library
            clearance_data['library']['documents'].append({
                'title': doc.title,
                'approved': doc.library_approved,
                'approved_by': doc.library_approved_by.username if doc.library_approved_by else None
            })

            # Sport Director
            clearance_data['sport_director']['documents'].append({
                'title': doc.title,
                'approved': doc.sport_director_approved,
                'approved_by': doc.sport_director_approved_by.username if doc.sport_director_approved_by else None
            })

            # Student Affairs
            clearance_data['student_affair']['documents'].append({
                'title': doc.title,
                'approved': doc.student_affair_approved,
                'approved_by': doc.student_affair_approved_by.username if doc.student_affair_approved_by else None
            })

            # Exam & Records
            clearance_data['exam_record']['documents'].append({
                'title': doc.title,
                'approved': doc.Exam_and_record_approved,
                'approved_by': doc.Exam_and_record_approved_by.username if doc.Exam_and_record_approved_by else None
            })

            # Hostel
            clearance_data['hostel']['documents'].append({
                'title': doc.title,
                'approved': doc.hostel_approved,
                'approved_by': doc.hostel_approved_by.username if doc.hostel_approved_by else None
            })

        # Now determine overall approval status for each department
        # A department is only approved if ALL documents are approved
        for dept_key, dept_data in clearance_data.items():
            if dept_data['documents']:
                all_approved = all(doc['approved'] for doc in dept_data['documents'])
                if all_approved:
                    dept_data['status'] = 'approved'
                    dept_data['approved'] = True
                else:
                    dept_data['status'] = 'pending'
                    dept_data['approved'] = False
            else:
                dept_data['status'] = 'no_documents'
                dept_data['approved'] = False

        # Get feedback/reviews for each department
        for doc in documents:
            reviews = Review.objects.filter(document=doc, student=request.user)
            for review in reviews:
                reviewer_position = getattr(review.reviewer, 'position', None)
                if reviewer_position == 'hod':
                    clearance_data['hod']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'sug':
                    clearance_data['sug']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'library':
                    clearance_data['library']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'sport_director':
                    clearance_data['sport_director']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'student_affair':
                    clearance_data['student_affair']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'exams_records':
                    clearance_data['exam_record']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })
                elif reviewer_position == 'hostel':
                    clearance_data['hostel']['feedback'].append({
                        'message': review.message,
                        'date': review.created_at,
                        'reviewer': review.reviewer.username
                    })

        # Determine overall clearance status
        overall_status = profile.overall_clearance_status

        return render(request, 'dashboard/dashboard.html', context = {
            "profile": profile,
            "clearance_data": clearance_data,
            "overall_status": overall_status,
            "documents": documents
        })



    elif request.user.position == "hod":
        profile = Hod.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids, department=profile.department)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "sport_director":
        profile = Sport_director.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "exams_records":
        profile = Exam_and_record.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "hostel":
        profile = Hostel.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "library":
        profile = Library.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "student_affair":
        profile = Student_affair.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})


    elif request.user.position == "sug":
        profile = Sug.objects.get(user = request.user)

        student_ids = Document.objects.values_list('student_id', flat=True).distinct()
        students = Student.objects.filter(id__in=student_ids)

        return render(request, 'dashboard/dashboard.html', context = {"profile" : profile, "students": students})



    return render(request, 'dashboard/dashboard.html', context = {"profile" : profile})


















def register(request):
    departments = Department.objects.all()
    levels = Level.objects.values_list('title', flat=True)

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        mat_no = request.POST.get('mat_no')
        email = request.POST.get('email')
        password = request.POST.get('password')
        department_id = request.POST.get('department')
        level_title = request.POST.get('level')
        first_hostel_room_no = request.POST.get('first_hostel_room_no')
        last_hostel_room_no = request.POST.get('last_hostel_room_no')
        date_of_completion = request.POST.get('date_of_completion')

        # Basic validation
        if not all([fullname, mat_no, email, password, department_id, level_title, date_of_completion]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'auth/register.html', {
                'departments': departments,
                'levels': levels
            })

        try:
            # Check if student with this matric number already exists
            if Student.objects.filter(mat_no=mat_no).exists():
                messages.error(request, 'A student with this matric number already exists.')
                return render(request, 'auth/register.html', {
                    'departments': departments,
                    'levels': levels
                })

            # Check if user with this email already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'auth/register.html', {
                    'departments': departments,
                    'levels': levels
                })

            # Get department and level objects
            department = Department.objects.get(id=department_id)
            level = Level.objects.get(title=level_title)

            # Create unique username
            import random
            username_unique = str(mat_no) + "_" + str(random.randint(1000, 9999))

            # Ensure username is truly unique
            while CustomUser.objects.filter(username=username_unique).exists():
                username_unique = str(mat_no) + "_" + str(random.randint(1000, 9999))

            # Create user with signal skip flag
            user = CustomUser(
                username=username_unique,
                email=email,
                first_name=fullname,
                position='student'
            )
            user.set_password(password)
            user._skip_signal = True  # Skip signal for registration
            user.save()

            # Manually create student profile with all required fields
            Student.objects.create(
                user=user,
                mat_no=mat_no,
                department=department,
                level=level,
                first_hostel_room_no=first_hostel_room_no,
                last_hostel_room_no=last_hostel_room_no,
                date_of_completion=date_of_completion
            )

            messages.success(request, f'Account created successfully for {fullname}! Please log in with your matric number: {mat_no}')
            return redirect('login')

        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'auth/register.html', {
                'departments': departments,
                'levels': levels
            })

    return render(request, 'auth/register.html', {
        'departments': departments,
        'levels': levels
    })


def index(request):
    """Landing page view"""
    return render(request, 'index.html')


def debug_register(request):
    """Debug view to test registration components"""
    try:
        departments = Department.objects.all()
        levels = Level.objects.all()

        context = {
            'departments_count': departments.count(),
            'levels_count': levels.count(),
            'departments': departments,
            'levels': levels,
        }

        return render(request, 'debug.html', context)
    except Exception as e:
        return render(request, 'debug.html', {'error': str(e)})


def modern_login(request):
    """Modern login view using new template"""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email_or_matno = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email_or_matno or not password:
            messages.error(request, "Please enter both email/matric number and password.")
            return render(request, 'auth/new_login.html')

        try:
            # Try to find user by email first
            if "@" in email_or_matno:
                customuser = CustomUser.objects.get(email=email_or_matno.lower())
            else:
                # Try to find by matric number (check Student model)
                student = Student.objects.get(mat_no=email_or_matno)
                customuser = student.user

            # Authenticate with username
            user = authenticate(username=customuser.username, password=password)
            if user is not None:
                log(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid password.")

        except (CustomUser.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "No account found with this email or matric number.")
        except Exception as e:
            messages.error(request, "Login failed. Please try again.")

    return render(request, 'auth/new_login.html')


def modern_register(request):
    """Modern register view using new template"""
    try:
        departments = Department.objects.all()
        levels = Level.objects.values_list('title', flat=True)
    except Exception as e:
        messages.error(request, f'Database error: {str(e)}')
        return render(request, 'auth/new_register.html', {
            'departments': [],
            'levels': []
        })

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        mat_no = request.POST.get('mat_no')
        email = request.POST.get('email')
        password = request.POST.get('password')
        department_id = request.POST.get('department')
        level_title = request.POST.get('level')
        first_hostel_room_no = request.POST.get('first_hostel_room_no')
        last_hostel_room_no = request.POST.get('last_hostel_room_no')
        date_of_completion = request.POST.get('date_of_completion')

        # Basic validation
        if not all([fullname, mat_no, email, password, department_id, level_title, date_of_completion]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'auth/new_register.html', {
                'departments': departments,
                'levels': levels
            })

        try:
            # Check if student with this matric number already exists
            if Student.objects.filter(mat_no=mat_no).exists():
                messages.error(request, 'A student with this matric number already exists.')
                return render(request, 'auth/new_register.html', {
                    'departments': departments,
                    'levels': levels
                })

            # Check if user with this email already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return render(request, 'auth/new_register.html', {
                    'departments': departments,
                    'levels': levels
                })

            # Get department and level objects
            department = Department.objects.get(id=department_id)
            level = Level.objects.get(title=level_title)

            # Create unique username
            import random
            username_unique = str(mat_no) + "_" + str(random.randint(1000, 9999))

            # Ensure username is truly unique
            while CustomUser.objects.filter(username=username_unique).exists():
                username_unique = str(mat_no) + "_" + str(random.randint(1000, 9999))

            # Create user with signal skip flag
            user = CustomUser(
                username=username_unique,
                email=email,
                first_name=fullname,
                position='student'
            )
            user.set_password(password)
            user._skip_signal = True  # Skip signal for registration
            user.save()

            # Manually create student profile with all required fields
            Student.objects.create(
                user=user,
                mat_no=mat_no,
                department=department,
                level=level,
                first_hostel_room_no=first_hostel_room_no,
                last_hostel_room_no=last_hostel_room_no,
                date_of_completion=date_of_completion
            )

            messages.success(request, f'Account created successfully for {fullname}! Please log in with your matric number: {mat_no}')
            return redirect('login')

        except Exception as e:
            # Clean up any created user if student creation failed
            try:
                if 'user' in locals():
                    user.delete()
            except:
                pass

            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'auth/new_register.html', {
                'departments': departments,
                'levels': levels,
                'form_data': {
                    'fullname': fullname,
                    'mat_no': mat_no,
                    'email': email,
                    'department_id': department_id,
                    'level_title': level_title,
                    'first_hostel_room_no': first_hostel_room_no,
                    'last_hostel_room_no': last_hostel_room_no,
                    'date_of_completion': date_of_completion
                }
            })

    return render(request, 'auth/new_register.html', {
        'departments': departments,
        'levels': levels
    })















def upload_doc(request):
    if request.method == 'POST':
        title_id = request.POST['title']
        file = request.FILES['file']
        student = Student.objects.get(user=request.user)
        from .models import DocTitle, CustomUser, Hod
        try:
            doc_title = DocTitle.objects.get(id=title_id)
        except DocTitle.DoesNotExist:
            messages.error(request, "Invalid document title selected.")
            return redirect('upload_doc')

        document = Document(
            title=doc_title,
            file=file,
            student=student
        )
        document.save()

        # Email notification to HOD of student's department and all other staff (excluding students)
        from django.conf import settings
        from django.apps import apps
        User = settings.AUTH_USER_MODEL
        UserModel = apps.get_model(*User.split('.'))

        # Get HOD for student's department
        hod_email = None
        try:
            hod = Hod.objects.get(department=student.department)
            if hod.user.email:
                hod_email = hod.user.email
        except Hod.DoesNotExist:
            hod_email = None

        # Get all other staff emails (excluding students and HODs)
        staff_emails = list(UserModel.objects.exclude(position__in=['student', 'hod']).values_list('email', flat=True))

        # Compose recipient list: HOD (if exists) + other staff
        recipient_emails = []
        if hod_email:
            recipient_emails.append(hod_email)
        recipient_emails.extend([email for email in staff_emails if email])

        if recipient_emails:
            from django.core.mail import send_mail
            subject = 'New Document Uploaded'
            message = f'A new document titled "{doc_title.title}" has been uploaded by {student.user.username}.'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_emails,
                fail_silently=True
            )

        messages.success(request, "Document Uploaded Successfully ")
        return redirect('upload_doc')

    from .models import DocTitle
    doc_titles = DocTitle.objects.all()
    return render(request, 'dashboard/upload_doc.html', {'doc_titles': doc_titles})




def remove_doc(request, doc_id):
    document = Document.objects.get(id=doc_id)
    document.delete()
    messages.success(request, "Document Deleted Successfully")
    return redirect('my_doc')



def my_doc(request):
    student = Student.objects.get(user=request.user)

    document = Document.objects.filter(student = student)

    context = {
        'documents': document
    }
    return render(request, 'dashboard/my_doc.html', context)






def send_doc(request):
    return render(request, 'base.html')






@login_required(login_url="login")
def student_doc(request):
    user = request.user
    form = StatementResultForm()


    # Get all distinct student IDs that have a document
    student_ids = Document.objects.values_list('student_id', flat=True).distinct()

    if user.position == "hod":
        # Get HOD's department (assuming it's stored in their profile)
        try:
            hod_profile = get_object_or_404(Hod, user=user)  # or whatever model stores their department
            students = Student.objects.filter(
                id__in=student_ids,
                department=hod_profile.department
            )
        except:
            messages.error(request, "Unable to find your department info.")
            students = Student.objects.none()
    else:
        # For other users (non-HODs), show all students with documents
        students = Student.objects.filter(id__in=student_ids)

    context = {
        'students': students,
        'form': form
    }

    return render(request, 'dashboard/student_doc.html', context)





def view_student_docs(request, student_id):
    student = Student.objects.get(id=student_id)
    documents = Document.objects.filter(student=student)

    context = {
        'student': student,
        'documents': documents
    }
    return render(request, 'dashboard/student_documents.html', context)









def approve_doc(request, doc_id, field):
    doc = get_object_or_404(Document, id=doc_id)
    profile, created = Student.objects.get_or_create(user=request.user)
    student_user = doc.student  # Assuming Document model has a ForeignKey to User as 'student'

    # Define readable names for fields
    field_names = {
        'hod_approved': 'HOD',
        'student_affair_approved': 'Student Affairs',
        'hostel_approved': 'Hostel Warden',
        'sug_approved': 'Entrepreneurship',
        'library_approved': 'Library',
        'sport_director_approved': 'Sport Director',
        'Exam_and_record_approved': 'Exams & Records'
    }

    if field in field_names:
        setattr(doc, field, True)
        setattr(doc, f"{field}_by", request.user)
        doc.save()

        approver_title = field_names[field]
        subject = f"Approval of your document by {approver_title}"
        message = (
            f"Dear {student_user.user.username},\n\n"
            f"Your document titled '{doc.title}' has been approved by the {approver_title}.\n"
            f"Please log in to your dashboard to view the updated status.\n\n"
            "Best regards,\n"
            f"{approver_title} Office"
        )
        recipient = [student_user.user.email]

        # Send email only if user has an email set
        if student_user.user.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)

        messages.success(request, f"{approver_title} Approval Successful.")
    else:
        messages.error(request, "Invalid approval field.")

    return redirect(request.META.get('HTTP_REFERER', '/'))








def disapprove_doc(request, doc_id, field):
    doc = get_object_or_404(Document, id=doc_id)
    student_user = doc.student.user  # Assuming `student` is a ForeignKey to `User` in Document model


    field_names = {
        'hod_approved': 'HOD',
        'student_affair_approved': 'Student Affairs',
        'hostel_approved': 'Hostel Warden',
        'sug_approved': 'Entrepreneurship',
        'library_approved': 'Library',
        'sport_director_approved': 'Sport Director',
        'Exam_and_record_approved': 'Exams & Records'
    }

    if field in field_names:
        setattr(doc, field, False)
        setattr(doc, f"{field}_by", None)
        doc.save()

        approver_title = field_names[field]
        messages.success(request, f"{approver_title} disapproved the document.")

        # ✅ Send email notification
        if student_user.email:
            subject = f"Your Document Was Disapproved by {approver_title}"
            message = (
                f"Dear {student_user.get_full_name() or student_user.username},\n\n"
                f"Your document titled '{doc.title}' was reviewed and disapproved by the {approver_title}.\n"
                "Please log in to your portal to make the necessary corrections and resubmit.\n\n"
                "Best regards,\n"
                f"{approver_title} Office"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
    else:
        messages.error(request, "Invalid approval field.")

    return redirect(request.META.get('HTTP_REFERER', '/'))










@login_required(login_url='login')
def profile(request):
    user = request.user
    position = user.position.lower()

    profile_model = {
        'hod': Hod,
        'sug': Sug,
        'sport_director': Sport_director,
        'library': Library,
        'hostel': Hostel,
        'student_affair': Student_affair,
        'exams_records': Exam_and_record,
    }.get(position)

    form_class = {
        'hod': HodForm,
        'sug': SugForm,
        'sport_director': SportDirectorForm,
        'library': LibraryForm,
        'hostel': HostelForm,
        'student_affair': StudentAffairForm,
        'exams_records': ExamAndRecordForm,
    }.get(position)


    if not profile_model or not form_class:
        return render(request, 'dashboard/profile.html', {'error': 'Unsupported role'})

    profile_instance = get_object_or_404(profile_model, user=user)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile_instance, user=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(request, 'dashboard/profile.html', {'form': form, 'profile': profile_instance})
    else:
        form = form_class(instance=profile_instance, user=user)

    return render(request, 'dashboard/profile.html', {
        'form': form,
        'profile': profile_instance,
    })














@login_required
def student_profile(request):
    try:
        student, created = Student.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('student_profile')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        else:
            form = StudentProfileForm(instance=student)

        return render(request, 'dashboard/student-profile.html', {'form': form, 'profile': student})

    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return redirect('dashboard')









def login(request):
    if request.user.is_anonymous:
        if request.method == "POST":
                email = request.POST["email"].lower()
                password = request.POST["password"]
                try:
                    customuser = CustomUser.objects.get(email=email)
                    user = authenticate(username=customuser.username, password=password)  # Authenticate with email
                    if user is not None:
                        log(request, user)
                        messages.success(request, "Login successful!")
                        return redirect("dashboard")  # Redirect to home page or any other desired page
                    else:
                        messages.error(request, "Invalid email or password")
                except :
                    messages.error(request, "Invalid email or password")
                    return redirect('login')
    else:
        return redirect("dashboard")




    return render(request, 'auth/login.html')











def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')








@login_required(login_url="login")
def statement_result(request):
    # Only allow students to view their statement
    if request.user.position != "student":
        messages.error(request, "Only students can view their Statement of Result.")
        return redirect("dashboard")

    try:
        student_profile = get_object_or_404(Student, user=request.user)

        try:
            # Try to get the statement linked to the logged-in user
            statement = Statement_Result.objects.get(student=student_profile)

            context = {
                'statement': statement,
                'student_profile': student_profile,
                'results': [],  # Replace with real results if needed
                'today': statement.created,  # ✅ Use issued date from the model
                'not_generated': False
            }
            return render(request, 'dashboard/statement_result.html', context)

        except Statement_Result.DoesNotExist:
            # Statement not yet generated
            messages.info(request, "Your Statement of Result has not been generated yet.")
            context = {
                'statement': None,
                'student_profile': student_profile,
                'results': [],
                'today': None,  # No date since there's no statement
                'not_generated': True
            }
            return render(request, 'dashboard/statement_result.html', context)

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")









from .forms import StatementResultForm



@login_required(login_url="login")
def create_statement_of_result(request, student_id):
    if request.user.position != "exams_records":
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('student_doc')

    student_profile = get_object_or_404(Student, id=student_id)
    student_user = student_profile.user

    if student_profile.overall_clearance_status != "Completely Approved":
        messages.error(
            request,
            f"Cannot generate Statement of Result. {student_user.username}'s clearance is still in progress."
        )
        return redirect('student_doc')

    if Statement_Result.objects.filter(student=student_profile).exists():
        messages.info(
            request,
            f"Statement of Result has already been generated for {student_user.username}."
        )
        return redirect('student_doc')

    if request.method == 'POST':
        form = StatementResultForm(request.POST)
        if form.is_valid():
            sor = form.save(commit=False)
            sor.student = student_profile
            sor.issued_by = request.user
            sor.signature_1 = getattr(student_profile, 'signature', None)
            sor.signature_2 = getattr(student_profile, 'signature', None)
            sor.save()

            messages.success(
                request,
                f"Statement of Result generated successfully for {student_user.username}."
            )

            # Send email
            if student_user.email:
                subject = "Your Statement of Result Has Been Generated"
                message = (
                    f"Dear {student_user.username},\n\n"
                    f"Your Statement of Result has been successfully generated.\n"
                    f"You can now log in to your dashboard to view or download it.\n\n"
                    "Best regards,\n"
                    "Exams and Records Office"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
        else:
            messages.error(request, "Please correct the errors in the form.")

        return redirect('student_doc')

    return redirect('student_doc')









@login_required(login_url="login")
def view_clearance_detail(request, department):
    """View detailed clearance information for a specific department"""
    if request.user.position != "student":
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    profile = Student.objects.get(user=request.user)
    documents = Document.objects.filter(student=profile)

    # Department mapping
    dept_mapping = {
        'hod': {
            'name': 'Head of Department',
            'staff_name': 'Dr. Alice Johnson',
            'field': 'hod_approved',
            'approved_by_field': 'hod_approved_by',
            'position': 'hod'
        },
        'sug': {
            'name': 'Entrepreneurship',
            'staff_name': 'Michael Okon',
            'field': 'sug_approved',
            'approved_by_field': 'sug_approved_by',
            'position': 'sug'
        },
        'library': {
            'name': 'Library Officer',
            'staff_name': 'Mrs. Grace Edet',
            'field': 'library_approved',
            'approved_by_field': 'library_approved_by',
            'position': 'library'
        },
        'sport_director': {
            'name': 'Sport Director',
            'staff_name': 'Samuel Nwosu',
            'field': 'sport_director_approved',
            'approved_by_field': 'sport_director_approved_by',
            'position': 'sport_director'
        },
        'student_affair': {
            'name': 'Student Affairs',
            'staff_name': 'Blessing Chika',
            'field': 'student_affair_approved',
            'approved_by_field': 'student_affair_approved_by',
            'position': 'student_affair'
        },
        'exam_record': {
            'name': 'Exam & Records',
            'staff_name': 'Mrs. Rita Akpan',
            'field': 'Exam_and_record_approved',
            'approved_by_field': 'Exam_and_record_approved_by',
            'position': 'exams_records'
        },
        'hostel': {
            'name': 'Hostel Officer',
            'staff_name': 'Emmanuel Bassey',
            'field': 'hostel_approved',
            'approved_by_field': 'hostel_approved_by',
            'position': 'hostel'
        }
    }

    if department not in dept_mapping:
        messages.error(request, "Invalid department.")
        return redirect('dashboard')

    dept_info = dept_mapping[department]

    # Get document status for this department
    document_status = []
    for doc in documents:
        approved = getattr(doc, dept_info['field'])
        document_status.append({
            'title': doc.title,
            'approved': approved,
            'file': doc.file,
            'id': doc.id
        })

    # Get feedback for this department
    feedback_list = []
    for doc in documents:
        reviews = Review.objects.filter(
            document=doc,
            student=request.user,
            reviewer__position=dept_info['position']
        ).order_by('-created_at')

        for review in reviews:
            feedback_list.append({
                'message': review.message,
                'date': review.created_at,
                'reviewer': review.reviewer.username,
                'document_title': doc.title
            })

    # Determine overall status for this department
    # Only approved if ALL documents are approved
    all_approved = all(getattr(doc, dept_info['field']) for doc in documents) if documents else False
    has_documents = documents.exists()

    if not has_documents:
        dept_status = 'no_documents'
    elif all_approved:
        dept_status = 'approved'
    else:
        dept_status = 'pending'

    context = {
        'department': department,
        'dept_info': dept_info,
        'document_status': document_status,
        'feedback_list': feedback_list,
        'dept_status': dept_status,
        'profile': profile
    }

    return render(request, 'dashboard/clearance_detail.html', context)


def send_review(request, doc_id):
    if request.method == "POST":
        doc = get_object_or_404(Document, id=doc_id)
        student_user = doc.student.user
        reviewer = request.user
        message = request.POST.get('message')
        reviewer_position = getattr(reviewer, 'position', 'Reviewer')

        # Save to Review model
        Review.objects.create(
            reviewer=reviewer,
            student=student_user,
            document=doc,
            message=message
        )

        # Prepare and send email
        subject = f"Feedback on your document from {reviewer_position}"
        email_body = (
            f"Dear {student_user.username},\n\n"
            f"You have received a review regarding your document titled '{doc.title}'.\n\n"
            f"Reviewer ({reviewer_position}) says:\n\n"
            f"{message}\n\n"
            "Please log in to your dashboard for further updates.\n\n"
            "Best regards,\n"
            f"{reviewer_position} Position"
        )

        if student_user.email:
            send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
            messages.success(request, "Review sent and saved successfully.")
        else:
            messages.error(request, "Student has no email address on file.")

        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return redirect('/')














@login_required(login_url='login')
def statement_result_list(request):
    if request.user.position != 'exams_records':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    statements = Statement_Result.objects.select_related('student').all()
    return render(request, 'dashboard/statement_list.html', {'statements': statements})








@login_required(login_url='login')
def statement_result_detail(request, pk):
    statement = get_object_or_404(Statement_Result, pk=pk)
    student_profile = statement.student  # already a Student instance

    return render(request, 'dashboard/statement_preview.html', {
        'statement': statement,
        'student_profile': student_profile,
        'today': statement.created,
    })












@login_required(login_url="login")
def send_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.sender_position = request.user.position
            announcement.save()

            recipients = []

            if request.user.position == 'hod':
                try:
                    # Assuming you have a Hod model with department FK
                    hod_profile = request.user.hod  # replace if your related name is different
                    dept_students = Student.objects.filter(department=hod_profile.department)
                    recipients = [student.user for student in dept_students]
                except Exception as e:
                    messages.error(request, "Could not determine your department.")
                    recipients = []

            else:
                # Everyone else (e.g. student_affair) gets all students
                recipients = [student.user for student in Student.objects.all()]

            # Save recipients
            announcement.recipients.set(recipients)

            # Send emails
            for user in recipients:
                if user.email:
                    send_mail(
                        subject=announcement.title,
                        message=announcement.message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )

            messages.success(request, "Announcement sent successfully.")
            return redirect('dashboard')

    else:
        form = AnnouncementForm()

    return render(request, 'dashboard/send_announcement.html', {'form': form})
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def save_push_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('expo_push_token')
            if token:
                request.user.expo_push_token = token
                request.user.save()
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid request'}, status=400)
