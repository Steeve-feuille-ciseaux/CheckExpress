from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.accueil, name='accueil'),

    # Session
    path('session/creer/', views.creer_session, name='creer_session'),
    path('sessions/', views.liste_sessions, name='liste_sessions'), 
    path('session/<int:pk>/', views.voir_session, name='voir_session'),
    path('session-du-jour/', views.modifier_session_du_jour, name='modifier_session_du_jour'),
    path('session/modifier/<int:pk>/', views.modifier_session, name='modifier_session'),
    path('sessions/<int:pk>/supprimer/', views.confirmer_suppression_session, name='confirmer_suppression_session'),

    # Licencier
    path('licencies/ajouter/', views.ajouter_licencie, name='ajouter_licencie'),
    path('licencies/', views.liste_licencies, name='liste_licencies'),
    path('licencie/modifier/<int:licencie_id>/', views.modifier_licencie, name='modifier_licencie'),
    path('licencie/supprimer/<int:licencie_id>/', views.supprimer_licencie, name='supprimer_licencie'),
    path('licencies/export/', views.export_licencies_excel, name='export_licencies_excel'),

    path('presence/', views.enregistrer_presence, name='enregistrer_presence'),

    # Connection 
    path('utilisateurs/', views.voir_utilisateurs, name='voir_utilisateurs'),
    path('ajouter-utilisateur/', views.ajouter_utilisateur_prof, name='ajouter_utilisateur_prof'),
    path('ajouter-ville/', views.ajouter_ville, name='ajouter_ville'),
    path('ajouter-etablissement/', views.ajouter_etablissement, name='ajouter_etablissement'),
    path('ajouter-role/', views.ajouter_role, name='ajouter_role'),
    path('login/', auth_views.LoginView.as_view(template_name='presence/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
]
