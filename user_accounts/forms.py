from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'mat_no', 'department', 'level',
             'image',
        'signature'
        ]

        widgets = {
            'mat_no': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'signature': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields not required for profile updates
        if self.instance and self.instance.pk:
            self.fields['mat_no'].required = False
            self.fields['department'].required = False
            self.fields['level'].required = False


class StudentProfileForm(forms.ModelForm):
    """Separate form for profile updates - only editable fields"""
    class Meta:
        model = Student
        fields = ['image']

        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'signature': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }





from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message']


    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['message'].widget.attrs.update({'class': 'form-control'})















from .models import Statement_Result, AcademicSession

class StatementResultForm(forms.ModelForm):
    class Meta:
        model = Statement_Result
        fields = ['programme', 'grade', 'academic_session']
        widgets = {
            'programme': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'academic_session': forms.Select(attrs={'class': 'form-control'}),
        }





from django import forms
from .models import Hod, Sug, Sport_director, Library, Hostel, Student_affair, Exam_and_record

class ProfileBaseForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(disabled=True)  # still not editable
    username = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # store for saving later
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['username'].initial = self.user.username

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Update related CustomUser fields
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
                instance.user = self.user  # reassign user in case it's new

        if commit:
            instance.save()
        return instance





class HodForm(ProfileBaseForm):
    department = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = self.Meta.model._meta.get_field('department').remote_field.model.objects.all()

    class Meta:
        model = Hod
        fields = ['department', 'image']

class SugForm(ProfileBaseForm):
    class Meta:
        model = Sug
        fields = ['image']

class SportDirectorForm(ProfileBaseForm):
    class Meta:
        model = Sport_director
        fields = ['image']

class LibraryForm(ProfileBaseForm):
    class Meta:
        model = Library
        fields = ['image']

class HostelForm(ProfileBaseForm):
    class Meta:
        model = Hostel
        fields = ['image']

class StudentAffairForm(ProfileBaseForm):
    class Meta:
        model = Student_affair
        fields = ['image', 'signature']

class ExamAndRecordForm(ProfileBaseForm):
    class Meta:
        model = Exam_and_record
        fields = ['image']
