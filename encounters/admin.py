from django.contrib import admin
import datetime

# Register your models here.
from .models import Animal, Animal_Type, Encounter


class AnimalAdmin(admin.ModelAdmin):
    exclude = ('Inactive_Date',)
    list_filter = ['Animal_Type']

    # def get_queryset(self, request):
    #     qs = super(AnimalAdmin, self).get_queryset(request)
    #     return qs.filter(Inactive_Date != None)

admin.site.register(Animal_Type)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Encounter)