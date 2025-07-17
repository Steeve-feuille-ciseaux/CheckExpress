from django.db import models

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

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Presence(models.Model):
    licence = models.ForeignKey(Licence, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.licence} - {self.date} - {'Présent' if self.present else 'Absent'}"


class Session(models.Model):
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    theme = models.TextField()
    presences = models.ManyToManyField(Licence, blank=True)

    def __str__(self):
        return f"Session du {self.date} ({self.heure_debut} - {self.heure_fin})"
