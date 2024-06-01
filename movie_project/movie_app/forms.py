# forms.py
from django import forms
from .models import ProductionCompany

class ProductionCompanyForm(forms.ModelForm):
    class Meta:
        model = ProductionCompany
        fields = ['name', 'city', 'company_description']
