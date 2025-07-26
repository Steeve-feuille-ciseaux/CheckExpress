from django.db import models
from django.contrib.auth.models import User

class Ville(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Etablissement(models.Model):
    name = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='etablissements')
    adresse = models.CharField(max_length=255, blank=True, null=True)  # champ facultatif

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.SET_NULL, null=True, blank=True)

class Licence(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()

    GRADE_CHOICES = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
        ('Expert', 'Expert'),
    ]
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)

    etablissement = models.ForeignKey(
        Etablissement, on_delete=models.SET_NULL, null=True, blank=True, related_name='licences'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nom', 'prenom'], name='unique_nom_prenom')
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Presence(models.Model):
    licence = models.ForeignKey(Licence, on_delete=models.CASCADE, related_name='licencies')
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.licence} - {self.date} - {'Présent' if self.present else 'Absent'}"

class Session(models.Model):
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    theme = models.TextField(blank=True)
    presences = models.ManyToManyField(Licence, blank=True, related_name='sessions')

    created_by = models.ForeignKey(User, related_name='sessions_created', on_delete=models.SET_NULL, null=True, blank=True)
    checked_by = models.ForeignKey(User, related_name='sessions_checked', on_delete=models.SET_NULL, null=True, blank=True)

    etablissement = models.ForeignKey(Etablissement, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')

    def __str__(self):
        return f"Session du {self.date} ({self.heure_debut} - {self.heure_fin})"