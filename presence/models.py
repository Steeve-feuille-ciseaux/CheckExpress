from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f"Session du {self.date} ({self.heure_debut} - {self.heure_fin})"
