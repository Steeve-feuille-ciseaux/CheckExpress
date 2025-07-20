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

class LicenceForm(forms.ModelForm):
    class Meta:
        model = Licence
        fields = ['nom', 'prenom', 'date_naissance', 'grade']
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'  # ← important
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Forcer l'affichage au format HTML5 si instance existe
        if self.instance and self.instance.date_naissance:
            self.initial['date_naissance'] = self.instance.date_naissance.strftime('%Y-%m-%d')