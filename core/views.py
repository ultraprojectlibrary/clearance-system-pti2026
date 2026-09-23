from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from user_accounts.models import Student, Document

@login_required(login_url="login")
def view_student_docs(request, student_id):
    """View documents for a specific student (for staff)"""
    student = get_object_or_404(Student, id=student_id)
    documents = Document.objects.filter(student=student)

    context = {
        'student': student,
        'documents': documents
    }
    return render(request, 'dashboard/student_documents.html', context)


@login_required(login_url="login")
def approve_doc(request, doc_id, approval_stage_field):
    """Approve a document for a specific stage"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    doc = get_object_or_404(Document, id=doc_id)
    user = request.user

    # Map approval fields to user positions
    approval_mapping = {
        'hod_approved': 'hod',
        'sug_approved': 'sug',
        'library_approved': 'library',
        'sport_director_approved': 'sport_director',
        'student_affair_approved': 'student_affair',
        'Exam_and_record_approved': 'exams_records',
        'hostel_approved': 'hostel'
    }

    # Check if user has permission to approve this stage
    if approval_stage_field not in approval_mapping:
        return JsonResponse({'success': False, 'message': 'Invalid approval stage'})

    required_position = approval_mapping[approval_stage_field]
    if user.position != required_position:
        return JsonResponse({'success': False, 'message': 'You do not have permission to approve this stage'})

    # Set approval
    setattr(doc, approval_stage_field, True)

    # Set who approved it
    approved_by_field = approval_stage_field.replace('_approved', '_approved_by')
    if hasattr(doc, approved_by_field):
        setattr(doc, approved_by_field, user)

    doc.save()

    messages.success(request, f'Document "{doc.title}" has been approved.')
    return JsonResponse({'success': True, 'message': 'Document approved successfully'})
