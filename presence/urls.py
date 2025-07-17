from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('session/creer/', views.creer_session, name='creer_session'),
    path('session/modifier/<int:pk>/', views.modifier_session, name='modifier_session'),
    path('sessions/', views.liste_sessions, name='liste_sessions'), 
    path('presence/', views.enregistrer_presence, name='enregistrer_presence'),
    path('export/', views.export_presence_du_jour, name='export_presence_du_jour'),
]
