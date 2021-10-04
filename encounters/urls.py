#cfm created
from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('openencounter/', views.open_encounter, name='openencounter'),
    path('myencounters/', views.EncountersByUserListView.as_view(), name='my-encounters'),
    path('allencounters/', views.AllEncountersListView.as_view(), name='all-encounters'),
    path('encounter/<int:pk>', views.EncounterDetailView.as_view(), name = 'encounter-detail'),
    path('todaysencounters/', views.TodaysEncountersListView.as_view(), name='todays-encounters'),
    path('logout/', views.logout_view, name='logout'),
    path('export/', views.export_data_view, name = 'export'),
    path('api/load_animal_uses/', views.load_animal_uses, name='animal-data-API')
    
]