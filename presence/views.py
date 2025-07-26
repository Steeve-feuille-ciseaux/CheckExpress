import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import Licence, Presence, Session, Ville, Etablissement, User
from .forms import PresenceForm, SessionForm, LicenceForm, VilleForm, EtablissementForm, GroupForm, UserUpdateForm
from django.utils.timezone import localdate, localtime, now
from datetime import datetime, timedelta
from django.db.models import Count, Max
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import UserCreationWithGroupForm
from django.contrib.auth.forms import SetPasswordForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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
            return redirect('liste_sessions')
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
    
    # Sessions d'aujourd'hui
    sessions_today = Session.objects.filter(date=today).order_by('heure_debut')
    
    # Sessions futures (après aujourd'hui)
    sessions_futures = Session.objects.filter(date__gt=today).order_by('date', 'heure_debut')
    
    # Sessions passées (avant aujourd'hui)
    sessions_passees = Session.objects.filter(date__lt=today).order_by('-date', '-heure_debut')
    
    return render(request, 'presence/liste_sessions.html', {
        'sessions_today': sessions_today,
        'sessions_futures': sessions_futures,
        'sessions_passees': sessions_passees,
        'today': today,
    })

def voir_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    return render(request, 'presence/voir_session.html', {'session': session})

@login_required
def modifier_session(request, pk):
    session = get_object_or_404(Session, pk=pk)

    # Date et heure de la session (on combine date + heure_debut)
    session_datetime = datetime.combine(session.date, session.heure_debut)

    # Convertir en timezone-aware si nécessaire
    if timezone.is_naive(session_datetime):
        session_datetime = timezone.make_aware(session_datetime)

    # Vérifier si plus de 24h sont passées
    if now() > session_datetime + timedelta(hours=24):
        messages.error(request, "Impossible de modifier une session de plus de 24h.")
        return redirect('liste_sessions')

    # Logique existante
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

    # Calcul de la date/heure de début de session
    session_datetime = datetime.combine(session.date, session.heure_debut)

    # Rendre timezone-aware si nécessaire
    if timezone.is_naive(session_datetime):
        session_datetime = timezone.make_aware(session_datetime)

    # Bloquer suppression si plus de 24h
    if timezone.now() > session_datetime + timedelta(hours=24):
        messages.error(request, "Impossible de supprimer une session de plus de 24h.")
        return redirect('liste_sessions')

    # Suppression si autorisée
    if request.method == "POST":
        session.delete()
        messages.success(request, "La session a bien été supprimée.")
        return redirect('liste_sessions')

    return render(request, 'presence/confirmer_suppression_session.html', {'session': session})

# Licencier
@login_required
def ajouter_licencie(request):
    if request.method == 'POST':
        form = LicenceForm(request.POST)
        if form.is_valid():
            licence = form.save(commit=False)

            # Associer automatiquement l'établissement depuis le profil utilisateur
            profile = getattr(request.user, 'profile', None)
            if profile and profile.etablissement:
                licence.etablissement = profile.etablissement

            licence.save()
            return redirect('liste_licencies')
    else:
        form = LicenceForm()

    return render(request, 'presence/ajouter_licencie.html', {'form': form})

@login_required
def liste_licencies(request):
    user = request.user

    if user.is_superuser:
        licencies = Licence.objects.annotate(
            nb_presences=Count('sessions'),
            last_session_date=Max('sessions__date')
        )
    else:
        profile = getattr(user, 'profile', None)
        if profile and profile.etablissement:
            licencies = Licence.objects.filter(etablissement=profile.etablissement).annotate(
                nb_presences=Count('sessions'),
                last_session_date=Max('sessions__date')
            )
        else:
            licencies = Licence.objects.none()  # Aucun si pas d’établissement associé

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
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Licenciés"

    current_time = localtime(now())
    export_date = current_time.strftime('%d/%m/%Y')
    export_time = current_time.strftime('%H:%M:%S')
    user = request.user

    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    title_font = Font(bold=True, size=14)
    header_fill = PatternFill("solid", fgColor="4F81BD")  # bleu clair
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    # Largeur colonnes
    column_widths = [20, 20, 18, 20]
    start_col = 2  # Décalage à la colonne B pour marge à gauche

    def merge_and_center(row, text, col_start, col_end, font=None):
        ws.merge_cells(start_row=row, start_column=col_start, end_row=row, end_column=col_end)
        cell = ws.cell(row=row, column=col_start)
        cell.value = text
        cell.alignment = center_align
        if font:
            cell.font = font

    # Coordonnées utiles
    right_col = start_col + 3  # Colonne E (B=2 +3 = 5)
    left_col = start_col       # Colonne B

    # Infos utilisateur connecté
    profile = getattr(user, 'profile', None)
    etablissement = profile.etablissement.name if profile and profile.etablissement else "Non défini"
    role = user.groups.first().name if user.groups.exists() else "Aucun rôle"

    # Ligne 1 à 3 : infos à gauche (col B), sans fusion
    ws.cell(row=1, column=start_col, value=f"Exporté par : {user.get_full_name() or user.username}").alignment = left_align
    ws.cell(row=2, column=left_col, value=f"Rôle : {role}").alignment = left_align
    ws.cell(row=3, column=left_col, value=f"Établissement : {etablissement}").alignment = left_align

    # Ligne 1 à 2 : infos à droite (col E), sans fusion
    right_align = Alignment(horizontal='right', vertical='center')
    ws.cell(row=1, column=right_col, value=f"Date : {export_date}").alignment = right_align
    ws.cell(row=2, column=right_col, value=f"Heure : {export_time}").alignment = right_align

    # Ligne 4 : ligne vide (espace)
    # Ligne 5 : titre "Suivi de présence" centré sur colonnes B à E
    merge_and_center(5, "Suivi de présence", start_col, start_col + 3, font=title_font)

    # Ligne 6 : ligne vide (espace)

    # Ligne 7 : en-têtes du tableau
    headers = ['Nom', 'Prénom', 'participation', 'Dernière présence']
    for col_num, header in enumerate(headers, start_col):
        cell = ws.cell(row=7, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_align

    # Récupérer les licenciés
    licencies = Licence.objects.annotate(
        nb_presences=Count('sessions'),
        last_session_date=Max('sessions__date')
    )

    # Remplir les données à partir de la ligne 8
    for i, licencie in enumerate(licencies, start=8):
        ws.cell(row=i, column=start_col, value=licencie.nom).alignment = center_align
        ws.cell(row=i, column=start_col).border = border

        ws.cell(row=i, column=start_col + 1, value=licencie.prenom).alignment = center_align
        ws.cell(row=i, column=start_col + 1).border = border

        ws.cell(row=i, column=start_col + 2, value=licencie.nb_presences).alignment = center_align
        ws.cell(row=i, column=start_col + 2).border = border

        last_session = licencie.last_session_date.strftime("%Y-%m-%d") if licencie.last_session_date else " "
        ws.cell(row=i, column=start_col + 3, value=last_session).alignment = center_align
        ws.cell(row=i, column=start_col + 3).border = border

    # Ajuster la largeur des colonnes (colonnes B à E)
    for i, width in enumerate(column_widths, start_col):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Génération du nom de fichier
    filename = f"Kudo_{current_time.strftime('%d%m%Y')}_{current_time.strftime('%H%M%S')}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response

# Gestion prof
@login_required
@user_passes_test(lambda u: u.is_superuser)
def voir_utilisateurs(request):
    users = User.objects.prefetch_related('groups').filter(is_superuser=False).exclude(id=request.user.id)
    return render(request, 'presence/voir_utilisateurs.html', {'users': users})

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'presence/user_detail.html', {'user_obj': user})

@login_required
def ajouter_utilisateur_prof(request):
    if not request.user.is_superuser:
        messages.warning(request, "Accès refusé")
        return redirect('accueil')  # redirige vers la page d'accueil

    if request.method == 'POST':
        form = UserCreationWithGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur ajouté avec succès.")
            return redirect('accueil')
    else:
        form = UserCreationWithGroupForm()

    return render(request, 'presence/ajouter_utilisateur.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    profile = getattr(user_obj, 'profile', None)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour avec succès.")
            return redirect('voir_utilisateurs')
    else:
        initial = {
            'etablissement': profile.etablissement if profile else None,
            'group': user_obj.groups.first()
        }
        form = UserUpdateForm(instance=user_obj, initial=initial)

    return render(request, 'presence/user_edit.html', {
        'form': form,
        'user_obj': user_obj
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Optionnel : Empêcher un superuser de se supprimer lui-même
        if user_obj == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect('voir_utilisateurs')

        user_obj.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
        return redirect('voir_utilisateurs')

    return render(request, 'presence/user_confirm_delete.html', {'user_obj': user_obj})

class SetPasswordForSelfView(LoginRequiredMixin, FormView):
    template_name = 'presence/set_password.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('user_detail')

    def get_form(self, form_class=None):
        return self.form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Mot de passe mis à jour avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.request.user  # Ajoute l'utilisateur au contexte
        return context

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'user_id': self.request.user.id})
    
class SetPasswordForOtherUserView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'presence/set_password.html'
    form_class = SetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        self.target_user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.target_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Le mot de passe de {self.target_user.username} a été mis à jour.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'user_id': self.target_user.id})

# gestion ville
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestion_ville(request):
    villes = Ville.objects.all()
    return render(request, 'presence/gestion_ville.html', {'villes': villes})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ajouter_ville(request):
    if request.method == 'POST':
        form = VilleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ville ajoutée avec succès.")
            return redirect('gestion_ville')
    else:
        form = VilleForm()
    return render(request, 'presence/ajouter_ville.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def modifier_ville(request, ville_id):
    ville = get_object_or_404(Ville, pk=ville_id)

    if request.method == 'POST':
        form = VilleForm(request.POST, instance=ville)
        if form.is_valid():
            form.save()
            messages.success(request, "Ville modifiée avec succès.")
            return redirect('gestion_ville')
    else:
        form = VilleForm(instance=ville)

    return render(request, 'presence/modifier_ville.html', {'form': form, 'ville': ville})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def supprimer_ville(request, ville_id):
    ville = get_object_or_404(Ville, pk=ville_id)

    if request.method == 'POST':
        ville.delete()
        messages.success(request, "Ville supprimée avec succès.")
        return redirect('gestion_ville')

    return render(request, 'presence/supprimer_ville.html', {'ville': ville})


# gestion établissement
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestion_etablissement(request):
    etablissements = Etablissement.objects.select_related('ville').all()
    return render(request, 'presence/gestion_etablissement.html', {'etablissements': etablissements})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ajouter_etablissement(request):
    if request.method == 'POST':
        form = EtablissementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Établissement ajouté avec succès.")
            return redirect('gestion_etablissement')
    else:
        form = EtablissementForm()
    return render(request, 'presence/ajouter_etablissement.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def modifier_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)

    if request.method == 'POST':
        form = EtablissementForm(request.POST, instance=etablissement)
        if form.is_valid():
            form.save()
            messages.success(request, "Établissement modifié avec succès.")
            return redirect('gestion_etablissement')
    else:
        form = EtablissementForm(instance=etablissement)

    return render(request, 'presence/modifier_etablissement.html', {'form': form, 'etablissement': etablissement})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def supprimer_etablissement(request, etablissement_id):
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)

    if request.method == 'POST':
        etablissement.delete()
        messages.success(request, "Établissement supprimé avec succès.")
        return redirect('gestion_etablissement')

    return render(request, 'presence/supprimer_etablissement.html', {'etablissement': etablissement})

# gestion role
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestion_role(request):
    groupes = Group.objects.all()
    return render(request, 'presence/gestion_role.html', {'groupes': groupes})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ajouter_role(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rôle (groupe) ajouté avec succès.")
            return redirect('gestion_role')
    else:
        form = GroupForm()

    return render(request, 'presence/ajouter_role.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def modifier_role(request, role_id):
    group = get_object_or_404(Group, pk=role_id)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Rôle mis à jour avec succès.")
            return redirect('gestion_role')
    else:
        form = GroupForm(instance=group)

    return render(request, 'presence/modifier_role.html', {'form': form, 'group': group})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def supprimer_role(request, role_id):
    group = get_object_or_404(Group, pk=role_id)

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Rôle supprimé avec succès.")
        return redirect('gestion_role')

    return render(request, 'presence/supprimer_role.html', {'group': group})