# forms.py
from django import forms
from .models import ProductionCompany,Movie,Person,Comment,Rating,SecurityQA
from django.contrib.auth.models import User


class ProductionCompanyForm(forms.ModelForm):
    class Meta:
        model = ProductionCompany
        fields = ['name', 'city', 'company_description']

class MovieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Dynamically set the required attribute of video_file based on whether it's for updating or creating
        is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)
        self.fields['video_file'].required = not is_update

    video_file = forms.FileField(label='Video File')

    class Meta:
        model = Movie
        fields = ['moviename', 'length', 'releaseyear', 'plot_summary', 'production_company']


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'birth_date', 'gender', 'marital_status']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')]),
            'marital_status': forms.Select(choices=[('S', 'Single'), ('M', 'Married'), ('W', 'Widowed'), ('U', 'Unknown')]),
        }
        
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
        }

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Current Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

class SecurityQAForm(forms.ModelForm):
    class Meta:
        model = SecurityQA
        fields = ['security_question', 'security_answer']

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    security_answer = forms.CharField(label='Security Answer')

class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")