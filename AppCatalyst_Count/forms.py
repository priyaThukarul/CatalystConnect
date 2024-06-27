from django import forms
from .models import Company_data

class QueryForm(forms.Form):
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter keyword'}))

    city = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'placeholder': 'Select City'})
    )

    employees_from = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Employees From'}))
    employees_to = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Employees To'}))
    
    industry = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'placeholder': 'Select Industry'})
    )
    
    year_founded = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'placeholder': 'Select Year Founded'})
    )
    
    state = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'placeholder': 'Select State'})
    )
    
    country = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'placeholder': 'Select Country'})
    )
    
    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.fields['city'].choices = self.get_choices(Company_data.objects.values_list('city', flat=True).distinct())
        self.fields['industry'].choices = self.get_choices(Company_data.objects.values_list('industry', flat=True).distinct())
        self.fields['year_founded'].choices = self.get_choices(Company_data.objects.values_list('year_founded', flat=True).distinct())
        self.fields['state'].choices = self.get_choices(Company_data.objects.values_list('state', flat=True).distinct())
        self.fields['country'].choices = self.get_choices(Company_data.objects.values_list('country', flat=True).distinct())

    def get_choices(self, values):
        choices = [(value, value) for value in values if value]  # filter out None or empty values
        choices.insert(0, ('', '---------'))  # Add empty option for select fields
        return choices
