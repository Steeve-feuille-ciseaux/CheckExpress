from django import forms
from .models import Session, Licence, Ville, Etablissement, Profile
from django.utils.html import format_html
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group, Permission


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Récupérer tous les objets Licence dans l'ordre du queryset
        self.licences = list(self.fields['presences'].queryset)

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

class UserCreationWithGroupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),  # tu peux filtrer ici si besoin
        required=True,
        label="Rôle (groupe)",
        help_text="Sélectionnez le rôle de l'utilisateur"
    )
    
    etablissement = forms.ModelChoiceField(
        queryset=Etablissement.objects.all(),
        required=False,
        label="Établissement",
        help_text="Sélectionnez l'établissement de l'utilisateur"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'group', 'etablissement', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            group = self.cleaned_data['group']
            user.groups.set([group])  # Remplace tous les groupes existants

            etablissement = self.cleaned_data.get('etablissement')
            Profile.objects.update_or_create(user=user, defaults={'etablissement': etablissement})

        return user
    
class VilleForm(forms.ModelForm):
    class Meta:
        model = Ville
        fields = ['name']

class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = ['name', 'ville', 'adresse']
        labels = {
            'adresse': 'Adresse (facultatif)',
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']