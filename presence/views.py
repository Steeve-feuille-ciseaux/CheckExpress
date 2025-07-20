import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import Licence, Presence, Session
from .forms import PresenceForm, SessionForm, LicenceForm
from django.utils.timezone import localdate, localtime
from datetime import datetime, timedelta
from django.db.models import Count, Max
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def accueil(request):
    today = localdate()
    now = localtime()
    sessions_today = Session.objects.filter(date=today)
    sessions = Session.objects.exclude(date=today).order_by('-date')

    return render(request, 'presence/accueil.html', {'sessions_today': sessions_today, 'sessions': sessions, 'today': today, 'now': now,})

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
            return redirect('accueil')
    else:
        initial = {}
        date_from_get = request.GET.get("date")
        heure_debut_from_get = request.GET.get("heure_debut")

        if date_from_get:
            initial["date"] = date_from_get

        if heure_debut_from_get:
            try:
                heure_debut_obj = datetime.strptime(heure_debut_from_get, "%H:%M")
                initial["heure_debut"] = heure_debut_obj.time()
                
                # Ajouter 2h à l'heure de début
                heure_fin_obj = (heure_debut_obj + timedelta(hours=2)).time()
                initial["heure_fin"] = heure_fin_obj
            except ValueError:
                pass  # en cas de format incorrect, on ignore et laisse vide

        form = SessionForm(initial=initial)

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
    now = localtime().time()

    # Rechercher la session du jour qui est en cours (heure_debut <= now < heure_fin)
    session = (
        Session.objects
        .filter(date=today, heure_debut__lte=now, heure_fin__gt=now)
        .order_by('heure_debut')
        .first()
    )

    # Si aucune session "en cours", afficher la plus proche à venir aujourd'hui
    if not session:
        session = (
            Session.objects
            .filter(date=today, heure_debut__gte=now)
            .order_by('heure_debut')
            .first()
        )

    # Si toujours rien, afficher la première de la journée passée
    if not session:
        session = (
            Session.objects
            .filter(date=today)
            .order_by('heure_debut')
            .first()
        )
    
    # Si aucune session "en cours", créer un pour aujourd'hui
    if not session:
        today = localdate()
        return render(request, 'presence/session_du_jour.html', {
            'session': None,
            'today': today,
            'now': now,
        })

    if not session:
        return render(request, 'presence/session_du_jour.html', {'session': None})

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

    return render(request, 'presence/session_du_jour.html', {'form': form, 'session': session})

@login_required
def confirmer_suppression_session(request, pk):
    session = get_object_or_404(Session, pk=pk)

    if request.method == "POST":
        session.delete()
        messages.success(request, "La session a bien été supprimée.")
        return redirect('liste_sessions')

    return render(request, 'presence/confirmer_suppression_session.html', {'session': session})

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
        nb_presences=Count('sessions'),
        last_session_date=Max('sessions__date')
    )
    return render(request, 'presence/liste_licencies.html', {'licencies': licencies})

@login_required
def modifier_licencie(request, licencie_id):
    licencie = get_object_or_404(Licence, pk=licencie_id)

    if request.method == 'POST':
        form = LicenceForm(request.POST, instance=licencie)
        if form.is_valid():
            form.save()
            return redirect('liste_licencies')
    else:
        form = LicenceForm(instance=licencie)

    return render(request, 'presence/modifier_licencie.html', {'form': form, 'licencie': licencie})

@login_required
def supprimer_licencie(request, licencie_id):
    licencie = get_object_or_404(Licence, pk=licencie_id)

    if request.method == 'POST':
        licencie.delete()
        messages.success(request, f"Licencié {licencie.prenom} {licencie.nom} supprimé.")
        return redirect('liste_licencies')

    return render(request, 'presence/confirmer_suppression_licencie.html', {'licencie': licencie})

# Export data 
@login_required
def export_licencies_excel(request):
    import openpyxl
    from django.utils.timezone import localtime, now

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Licenciés"

    # Date et heure locale au moment de l'export
    current_time = localtime(now())
    export_date = current_time.strftime('%d/%m/%Y')
    export_time = current_time.strftime('%H:%M:%S')

    # User connecté
    user = request.user

    # Infos en haut du fichier
    ws.append([f"Exporté par : {user.get_full_name() or user.username}"])
    ws.append([f"Date d'export : {export_date}"])
    ws.append([f"Heure d'export : {export_time}"])
    ws.append([])  # ligne vide avant le tableau

    # En-têtes du tableau
    ws.append(['Nom', 'Prénom', 'Nombre de présences', 'Dernière session'])

    licencies = Licence.objects.annotate(
        nb_presences=Count('sessions'),
        last_session_date=Max('sessions__date')
    )
    for licencie in licencies:
        ws.append([
            licencie.nom,
            licencie.prenom,
            licencie.nb_presences,
            licencie.last_session_date.strftime("%Y-%m-%d") if licencie.last_session_date else "Aucune session"
        ])

    # Génération du nom de fichier avec date et heure sans tirets
    filename = f"Kudo_{current_time.strftime('%d%m%Y')}_{current_time.strftime('%H%M%S')}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response