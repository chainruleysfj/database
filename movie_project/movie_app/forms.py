# forms.py
from django import forms
from .models import ProductionCompany,Movie

class ProductionCompanyForm(forms.ModelForm):
    class Meta:
        model = ProductionCompany
        fields = ['name', 'city', 'company_description']

class MovieForm(forms.ModelForm):
    video_file = forms.FileField(required=True, label='Video File')

    class Meta:
        model = Movie
        fields = ['moviename', 'length', 'releaseyear', 'plot_summary', 'production_company']