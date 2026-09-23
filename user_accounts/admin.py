from django.contrib import admin
from.models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'position', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'position')
    ordering = ('username',)



    # Fields to display when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'position', ),
        }),
    )

    # Optional: customize which fields are displayed in the admin form
    fieldsets = (
        (None, {'fields': ('username', 'email','first_name', 'last_name',  'password', 'position')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Sport_director)
admin.site.register(Student_affair)
admin.site.register(Hostel)
admin.site.register(Library)
admin.site.register(Exam_and_record)
admin.site.register(Hod)
admin.site.register(Sug)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student)
# admin.site.register(Sug_signing)
# admin.site.register(Sport_director_signing)
# admin.site.register(Hod_signing)
# admin.site.register(Student_affair_signing)
# admin.site.register(Hostel_signing)
# admin.site.register(Library_signing)
# admin.site.register(Exam_and_record_signing)
admin.site.register(Department)
admin.site.register(Level)
admin.site.register(Document)
admin.site.register(Statement_Result)
admin.site.register(Review)
admin.site.register(AcademicSession)
admin.site.register(DocTitle)