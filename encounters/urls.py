from os import name
from django.urls import path
from . import views
from django.contrib import admin

admin.site.site_header = "Animal Encounter Admin"
admin.site.site_title = "Animal Encounter Admin Portal"
admin.site.index_title = "Welcome to Animal Encounter Portal"

urlpatterns = [
    path('',views.index, name='index'),
    path('openencounter/', views.open_encounter, name='openencounter'),
    path('myencounters/', views.EncountersByUserListView.as_view(), name='my-encounters'),
    path('allencounters/', views.AllEncountersListView.as_view(), name='all-encounters'),
    path('encounter/<int:pk>', views.EncounterDetailView.as_view(), name = 'encounter-detail'),
    path('todaysencounters/', views.TodaysEncountersListView.as_view(), name='todays-encounters'),
    path('logout/', views.logout_view, name='logout'),
    #path('login/', views.login_view, name='login'),
    path('export/', views.export_data_view, name = 'export'),
    path('api/load_animal_uses/', views.load_animal_uses, name='animal-data-API'),
    path('animals/', views.AnimalTypes.as_view(), name='animal-types'),
    path('animallist/<str:animal_type>',views.AnimalTypesDetailView.as_view(), name = 'animallist'),
    path('encountersByAnimal/<str:pk>', views.EncountersByAnimalListView.as_view(), name= 'encounters-by-animal'),
    
]