from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import SetPasswordForOtherUserView

urlpatterns = [
    path('', views.accueil, name='accueil'),

    # Session
    path('session/creer/', views.creer_session, name='creer_session'),
    path('sessions/', views.liste_sessions, name='liste_sessions'), 
    path('session/<int:pk>/', views.voir_session, name='voir_session'),
    path('session-du-jour/', views.modifier_session_du_jour, name='modifier_session_du_jour'),
    path('session/modifier/<int:pk>/', views.modifier_session, name='modifier_session'),
    path('sessions/<int:pk>/supprimer/', views.confirmer_suppression_session, name='confirmer_suppression_session'),
    path("sessions/check-rapide/", views.check_rapide, name="check_rapide"),

    # Licencier
    path('licencies/ajouter/', views.ajouter_licencie, name='ajouter_licencie'),
    path('licencies/', views.liste_licencies, name='liste_licencies'),
    path('licencie/<int:licencie_id>/', views.detail_licencie, name='detail_licencie'),
    path('licencie/modifier/<int:licencie_id>/', views.modifier_licencie, name='modifier_licencie'),
    path('licencie/supprimer/<int:licencie_id>/', views.supprimer_licencie, name='supprimer_licencie'),
    path('licencies/export/', views.export_licencies_excel, name='export_licencies_excel'),

    path('presence/', views.enregistrer_presence, name='enregistrer_presence'),

    # Admin
    path('utilisateurs/', views.voir_utilisateurs, name='voir_utilisateurs'),
    path('utilisateur/<int:user_id>/', views.user_detail, name='user_detail'),
    path('ajouter-utilisateur/', views.ajouter_utilisateur_prof, name='ajouter_utilisateur_prof'),
    path('utilisateur/<int:user_id>/modifier/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    path('utilisateur/<int:user_id>/changer-mdp/', SetPasswordForOtherUserView.as_view(), name='user_password_change'),
    path('utilisateur/mot-de-passe/', views.SetPasswordForSelfView.as_view(), name='password_change'),

    # Ville
    path('gestion/ville/', views.gestion_ville, name='gestion_ville'),
    path('ajouter-ville/', views.ajouter_ville, name='ajouter_ville'),
    path('villes/modifier/<int:ville_id>/', views.modifier_ville, name='modifier_ville'),
    path('villes/supprimer/<int:ville_id>/', views.supprimer_ville, name='supprimer_ville'),
    
    # Dojo
    path('gestion/etablissement/', views.gestion_etablissement, name='gestion_etablissement'),
    path('ajouter-etablissement/', views.ajouter_etablissement, name='ajouter_etablissement'),
    path('etablissements/modifier/<int:etablissement_id>/', views.modifier_etablissement, name='modifier_etablissement'),
    path('etablissements/supprimer/<int:etablissement_id>/', views.supprimer_etablissement, name='supprimer_etablissement'),
    path('utilisateur/<int:user_id>/', views.user_detail, name='detail_utilisateur'),

    # Role
    path('gestion/role/', views.gestion_role, name='gestion_role'),
    path('ajouter-role/', views.ajouter_role, name='ajouter_role'),
    path('roles/modifier/<int:role_id>/', views.modifier_role, name='modifier_role'),
    path('roles/supprimer/<int:role_id>/', views.supprimer_role, name='supprimer_role'),
    
    path('login/', auth_views.LoginView.as_view(template_name='presence/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
]
