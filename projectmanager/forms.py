from django import forms
from .models import Project, Task

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
    