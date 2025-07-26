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
        queryset=Licence.objects.none(),  # initialement vide
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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Si user est fourni, filtrer les licences par établissement
        if user and hasattr(user, 'profile') and user.profile.etablissement:
            etablissement = user.profile.etablissement
            self.fields['presences'].queryset = Licence.objects.filter(etablissement=etablissement)
        else:
            # Sinon queryset vide ou toutes les licences si tu préfères
            self.fields['presences'].queryset = Licence.objects.none()
        
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
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    etablissement = forms.ModelChoiceField(queryset=Etablissement.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email']  # pas de password ici

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Mode édition : retire les champs de mot de passe
            self.fields.pop('password1', None)
            self.fields.pop('password2', None)
    
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

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Adresse email")
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Rôle (groupe)"
    )

    etablissement = forms.ModelChoiceField(
        queryset=Etablissement.objects.all(),
        required=False,
        label="Établissement"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'group', 'etablissement')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['group']])

            etablissement = self.cleaned_data.get('etablissement')
            Profile.objects.update_or_create(user=user, defaults={'etablissement': etablissement})

        return user