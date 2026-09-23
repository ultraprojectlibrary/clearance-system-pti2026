from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.conf import settings



class CustomUser(AbstractUser):
    POSITION_CHOICES = [
        ("student", "Student"),
        ("sug", "Entrepreneurship"),
        ("sport_director", "Sport Director"),
        ("exams_records", "Exams and Records"),
        ("hostel", "Hostel"),
        ("library", "Library"),
        ("student_affair", "Student Affairs"),
        ("hod", "HOD"),
    ]

    email = models.EmailField(
        _("email"),
        unique=True,
        help_text=_("Email required during registration"),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    username = models.CharField(unique=True, max_length=255)
    plaintext_password = models.CharField(
        max_length=128, blank=True, null=True, editable=False
    )
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="student",
        help_text=_("User's position in the institution"),
    )

    def __str__(self):
        return self.email

    image = models.ImageField(upload_to='profile/', null=True)
    expo_push_token = models.CharField(max_length=255, null=True, blank=True)




class Department(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



    

class Level(models.Model):
    title = models.CharField(max_length=100, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    mat_no = models.CharField(max_length=20, unique=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='profile_signature/', null=True, blank=True)
    first_hostel_room_no = models.CharField(max_length=50, null=True, blank=True)
    last_hostel_room_no = models.CharField(max_length=50, null=True, blank=True)
    date_of_completion = models.DateField(null=True, blank=True)


    @property
    def overall_clearance_status(self):
        documents = self.document_set.all()
        if not documents.exists():
            return "No Documents Uploaded"
        for doc in documents:
            if not doc.is_fully_approved:
                return "In Progress"
        return "Completely Approved"


    def __str__(self):
        return f"{self.user.username}"
    



class DocTitle(models.Model):
    title = models.CharField(max_length = 255, null = True)


    def __str__(self):
        return self.title










class Document(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='school_fee_receipts/', null=True)
    title = models.ForeignKey('DocTitle', on_delete = models.CASCADE, null = True, blank = True)
    # Approval fields
    hod_approved = models.BooleanField(default=False)
    sug_approved = models.BooleanField(default=False)
    hostel_approved = models.BooleanField(default=False)
    library_approved = models.BooleanField(default=False)
    sport_director_approved = models.BooleanField(default=False)
    Exam_and_record_approved = models.BooleanField(default=False) # Corresponds to 'exams_records' position
    student_affair_approved = models.BooleanField(default=False)
    # Fields to store who approved each stage
    hod_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hod_approved_documents')
    sug_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sug_approved_documents')
    hostel_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_approved_documents')
    library_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_approved_documents')
    sport_director_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sport_director_approved_documents')
    Exam_and_record_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_record_approved_documents')
    student_affair_approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_affair_approved_documents')


    @property
    def is_fully_approved(self):
        return all([
            self.hod_approved,
            self.sug_approved,
            self.hostel_approved,
            self.library_approved,
            self.sport_director_approved,
            self.Exam_and_record_approved,
            self.student_affair_approved,
        ])

    def __str__(self):
        return f"{self.title}========{self.student.user.username}"

    



class Hod(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"






class Sug(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    class Meta:
        verbose_name = "Entrepreneurship"
        verbose_name_plural = "Entrepreneurship"

    def __str__(self):
        return f"{self.user.username}========{self.user.get_position_display()}"

class Sport_director(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"

class Library(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"

class Hostel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"

class Student_affair(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"

class Exam_and_record(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}========{self.user.position}"













# Choices for grade
GRADE_CHOICES = [
    ('Distinction', 'Distinction'),
    ('Upper Credit', 'Upper Credit'),
    ('Lower Credit', 'Lower Credit'),
    ('Pass', 'Pass'),
]

# Choices for programme
PROGRAMME_CHOICES = [
    ('National Diploma', 'National Diploma'),
    ('Higher National Diploma', 'Higher National Diploma'),
]




class AcademicSession(models.Model):
    """Model to represent academic sessions like 2021/2022"""
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name



class Statement_Result(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
    issued_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='issued_results')

    signature_1 = models.FileField(upload_to='signatures/', null=True, blank=True)
    signature_2 = models.FileField(upload_to='signatures/', null=True, blank=True)

    programme = models.CharField(max_length=50, choices=PROGRAMME_CHOICES, null= True)
    grade = models.CharField(max_length=50, choices=GRADE_CHOICES, null=True)
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.SET_NULL, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.programme} Statement"






class Review(models.Model):
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reviews')
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} to {self.student.username}"











class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    sender_position = models.CharField(max_length=100)
    recipients = models.ManyToManyField(CustomUser, related_name='announcements')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.sender_position}"















# class Hod_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     departmental_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     nacos_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)







# class Sug_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     departmental_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     nacos_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)







# class Sport_director_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     departmental_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     nacos_due_receipt = models.FileField(upload_to='departmental_due_receipts/', null=True)
#     school_fee_receipt = models.FileField(upload_to='school_fee_receipts/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)








# class Library_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     approved = models.BooleanField(default=False)
#     school_fee_receipt = models.FileField(upload_to='school_fee_receipts/', null=True)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)





# class Hostel_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     school_fee_receipt = models.FileField(upload_to='school_fee_receipts/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)





# class Student_affair_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     school_fee_receipt = models.FileField(upload_to='school_fee_receipts/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)




# class Exam_and_record_signing(models.Model):
#     student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
#     waec_result = models.FileField(upload_to='waec_results/', null=True)
#     approved = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     date_signed = models.DateTimeField(auto_now=True)
