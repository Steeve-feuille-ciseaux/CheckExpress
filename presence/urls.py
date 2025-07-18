from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.accueil, name='accueil'),

    # Session
    path('session/creer/', views.creer_session, name='creer_session'),
    path('session/<int:pk>/', views.voir_session, name='voir_session'),
    path('session-du-jour/', views.modifier_session_du_jour, name='modifier_session_du_jour'),
    path('session/modifier/<int:pk>/', views.modifier_session, name='modifier_session'),
    path('sessions/', views.liste_sessions, name='liste_sessions'), 

    # Licencier
    path('licencies/', views.liste_licencies, name='liste_licencies'),
    path('licencies/ajouter/', views.ajouter_licencie, name='ajouter_licencie'),
    path('licencies/export/', views.export_licencies_excel, name='export_licencies_excel'),

    path('presence/', views.enregistrer_presence, name='enregistrer_presence'),
    path('export/', views.export_presence_du_jour, name='export_presence_du_jour'),

    # Connection 
    path('login/', auth_views.LoginView.as_view(template_name='presence/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accueil'), name='logout'),
]
