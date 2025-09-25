from django import forms

class ImportDataForm(forms.Form):
    file = forms.FileField()