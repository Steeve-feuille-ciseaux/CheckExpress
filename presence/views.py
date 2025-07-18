import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import Licence, Presence, Session
from .forms import PresenceForm, SessionForm, LicenceForm
from django.utils.timezone import localdate
from django.db.models import Count, Max
from django.contrib.auth.decorators import login_required

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

# Gestion des sessions
@login_required
def creer_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            session.save()
            form.save_m2m()
            return redirect('accueil') # Ou une autre vue de confirmation
    else:
        form = SessionForm()
    return render(request, 'presence/creer_session.html', {'form': form})

def liste_sessions(request):
    today = localdate()
    sessions = Session.objects.all().order_by('-date', '-heure_debut')
    sessions_today = sessions.filter(date=today)
    return render(request, 'presence/liste_sessions.html', {
        'sessions': sessions,
        'today': today,
        'sessions_today': sessions_today,
    })

def voir_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    return render(request, 'presence/voir_session.html', {'session': session})

@login_required
def modifier_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save(commit=False)
            session.checked_by = request.user
            session.save()
            form.save_m2m()
            return redirect('liste_sessions')
    else:
        form = SessionForm(instance=session)
    return render(request, 'presence/modifier_session.html', {'form': form, 'session': session})

@login_required
def modifier_session_du_jour(request):
    today = localdate()
    # On récupère la session du jour, s'il y en a plusieurs, on prend la première (ou adapte selon besoin)
    session = Session.objects.filter(date=today).first()
    
    if not session:
        return render(request, 'presence/session_du_jour.html', {'session': None})

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save(commit=False)
            session.checked_by = request.user
            session.save()
            form.save_m2m()
            return redirect('liste_sessions') # reload page après sauvegarde
    else:
        form = SessionForm(instance=session)

    return render(request, 'presence/session_du_jour.html', {'form': form, 'session': session})

# Licencier
def ajouter_licencie(request):
    if request.method == 'POST':
        form = LicenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_licencies')  # nom de la page liste licenciés
    else:
        form = LicenceForm()
    return render(request, 'presence/ajouter_licencie.html', {'form': form})

def liste_licencies(request):
    licencies = Licence.objects.annotate(
        nb_presences=Count('session'),
        last_session_date=Max('session__date')
    )
    return render(request, 'presence/liste_licencies.html', {'licencies': licencies})

def export_licencies_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Licenciés"

    ws.append(['Nom', 'Prénom', 'Nombre de présences', 'Dernière session'])

    licencies = Licence.objects.annotate(
        nb_presences=Count('session'),
        last_session_date=Max('session__date')
    )
    for licencie in licencies:
        ws.append([
            licencie.nom,
            licencie.prenom,
            licencie.nb_presences,
            licencie.last_session_date.strftime("%Y-%m-%d") if licencie.last_session_date else "Aucune session"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=licencies.xlsx'
    wb.save(response)
    return response

# Export data 
def export_licencies_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Licenciés"

    ws.append(['Nom', 'Prénom', 'Nombre de présences', 'Dernière session'])

    licencies = Licence.objects.annotate(
        nb_presences=Count('session_set'),
        last_session_date=Max('session_set__date')
    )
    for licencie in licencies:
        ws.append([
            licencie.nom,
            licencie.prenom,
            licencie.nb_presences,
            licencie.last_session_date.strftime("%Y-%m-%d") if licencie.last_session_date else "Aucune session"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=licencies.xlsx'
    wb.save(response)
    return response