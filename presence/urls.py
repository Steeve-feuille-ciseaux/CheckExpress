from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('session/creer/', views.creer_session, name='creer_session'),
    path('presence/', views.enregistrer_presence, name='enregistrer_presence'),
    path('export/', views.export_presence_du_jour, name='export_presence_du_jour'),
]
