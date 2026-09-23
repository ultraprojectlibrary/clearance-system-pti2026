from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Student, Hod, Sug, Sport_director, Library, Hostel, Student_affair, Exam_and_record

@receiver(post_save, sender=CustomUser)
def create_position_instance(sender, instance, created, **kwargs):
    if created:  # Ensure this runs only when a new user is created
        # Check if this is from admin creation (has a flag) or registration
        # Skip signal for registration (when _skip_signal is set)
        if getattr(instance, '_skip_signal', False):
            return

        position = instance.position.lower()

        if position == "student":
            Student.objects.create(user=instance)
        elif position == "sug":
            Sug.objects.create(user=instance)
        elif position == "sport_director":
            Sport_director.objects.create(user=instance)
        elif position == "exams_records":
            Exam_and_record.objects.create(user=instance)
        elif position == "hostel":
            Hostel.objects.create(user=instance)
        elif position == "library":
            Library.objects.create(user=instance)
        elif position == "student_affair":
            Student_affair.objects.create(user=instance)
        elif position == "hod":
            Hod.objects.create(user=instance)

post_save.connect(create_position_instance, sender=CustomUser)
