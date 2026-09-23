from django.urls import path
from . import views

app_name = 'core' # Add an app_name for namespacing if you prefer

urlpatterns = [
    # The URL from student_doc.html to view a specific student's documents
    path('student/<int:student_id>/documents/', views.view_student_docs, name='view_student_docs'),
    path('document/<int:doc_id>/approve/<str:approval_stage_field>/', views.approve_doc, name='approve_doc'),
]