from django import forms
from .models import Session, Licence

class PresenceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PresenceForm, self).__init__(*args, **kwargs)
        for licence in Licence.objects.all():
            self.fields[f'licence_{licence.id}'] = forms.BooleanField(
                label=f"{licence.prenom} {licence.nom}", required=False
            )

class SessionForm(forms.ModelForm):
    presences = forms.ModelMultipleChoiceField(
        queryset=Licence.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Licenciés présents"
    )

    class Meta:
        model = Session
        fields = ['date', 'heure_debut', 'heure_fin', 'theme', 'presences']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
            'theme': forms.Textarea(attrs={'rows': 3}),
        }
