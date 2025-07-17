import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Licence, Presence
from .forms import PresenceForm, SessionForm
from django.http import HttpResponse
import openpyxl

def accueil(request):
    return render(request, 'presence/accueil.html')

def export_presence_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Présences"

    # En-têtes
    sheet.append(['Nom', 'Prénom', 'Date', 'Présent'])

    # Données
    for p in Presence.objects.select_related('licence').all():
        sheet.append([
            p.licence.nom,
            p.licence.prenom,
            p.date.strftime("%Y-%m-%d"),
            "Oui" if p.present else "Non"
        ])

    # Réponse HTTP avec fichier
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=presences.xlsx'
    workbook.save(response)
    return response

def enregistrer_presence(request):
    if request.method == 'POST':
        form = PresenceForm(request.POST)
        if form.is_valid():
            date_aujourdhui = timezone.now().date()
            for licence in Licence.objects.all():
                key = f'licence_{licence.id}'
                present = form.cleaned_data.get(key, False)
                
                # Crée ou met à jour la présence du jour
                Presence.objects.update_or_create(
                    licence=licence,
                    date=date_aujourdhui,
                    defaults={'present': present}
                )
            return redirect('export_presence_du_jour')
    else:
        form = PresenceForm()
    return render(request, 'presence/presence_form.html', {'form': form})


def export_presence_du_jour(request):
    today = timezone.now().date()
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Présences"

    sheet.append(['Nom', 'Prénom', 'Date', 'Présent'])

    presences = Presence.objects.select_related('licence').filter(date=today)
    for p in presences:
        sheet.append([
            p.licence.nom,
            p.licence.prenom,
            p.date.strftime("%Y-%m-%d"),
            "Oui" if p.present else "Non"
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=presences_{today}.xlsx'
    workbook.save(response)
    return response

def creer_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accueil')  # Ou une autre vue de confirmation
    else:
        form = SessionForm()
    return render(request, 'presence/creer_session.html', {'form': form})