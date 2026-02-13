from django import forms
from .models import Project, Task
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'assigned_to']
        widgets = {'deadline': forms.DateInput(attrs={'type': 'date'})}
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)  # Projekt wird übergeben
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assigned_to'].queryset = project.team_members.all() 

class  ProjectForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Project
        fields = ['title', 'goal', 'start_date', 'end_date']

class AddMemberForm(forms.Form):
    email = forms.EmailField(label="User email")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user