# forms.py
from django import forms
from .models import ProductionCompany,Movie,Person

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
        


