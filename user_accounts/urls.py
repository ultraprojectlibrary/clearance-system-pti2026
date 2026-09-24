from django.urls import path
from .views import (
    register,
    login,
    modern_login,
    modern_register,
    debug_register,
    dashboard,
    upload_doc,
    my_doc,
    remove_doc,
    student_doc,
    view_student_docs,
    approve_doc,
    disapprove_doc,
    profile,
    student_profile,
    logout_view,
    statement_result,
    create_statement_of_result,
    send_review,
    statement_result_list,
    statement_result_detail,
    send_announcement,
    view_clearance_detail
)


# app_name = "user_accounts" # Define app_name for namespacing

urlpatterns = [
    path('', register, name='register_root'), # For root of /user/
    path('register/', modern_register, name='register'),  # Use modern register
    path('login/', modern_login, name='login'),  # Use modern login
    path('debug/', debug_register, name='debug_register'),  # Debug registration
    path('old-register/', register, name='old_register'),  # Keep old register as backup
    path('old-login/', login, name='old_login'),  # Keep old login as backup
    path('dashboard/', dashboard, name='dashboard'),
    
    path('upload-doc/', upload_doc, name='upload_doc'),
    path('my-doc/', my_doc, name='my_doc'),
    path('remove-doc/<str:doc_id>/', remove_doc, name='remove_doc'), # doc_id should likely be int
    
    path('student-doc/', student_doc, name='student_doc'), # Lists all students for staff
    path('student/<int:student_id>/docs/', view_student_docs, name='view_student_docs'), # Staff views specific student's docs
    path('approve/<int:doc_id>/<str:field>/', approve_doc, name='approve_doc'),
    path('disapprove/<int:doc_id>/<str:field>/', disapprove_doc, name='disapprove_doc'),
    
    path('profile/', profile, name='profile'), # Generic profile, might need specific logic or removal if student_profile is primary
    path('student/profile/', student_profile, name='student_profile'), # Student's own profile edit page
    path('logout/', logout_view, name='logout'),
    path('statement-result/', statement_result, name='statement_result'), # Student views their SOR
    path('student/<int:student_id>/create-statement/', create_statement_of_result, name='create_statement_of_result'), # Student Affairs generates SOR
    path('send-review/<int:doc_id>/', send_review, name='send_review'),
    path('statements/', statement_result_list, name='statement_list'),
    path('announcement/', send_announcement, name='send_announcement'),
    path('clearance/<str:department>/', view_clearance_detail, name='view_clearance_detail'),
    path('statements/', statement_result_list, name='statement_list'),
    path('statements/<int:pk>/view/', statement_result_detail, name='statement_detail'),

]
