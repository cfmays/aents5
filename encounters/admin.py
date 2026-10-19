from django.contrib import admin
import datetime

# Register your models here.
from .models import Animal, Animal_Type, Encounter


class InactiveFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [('active', 'Active'), ('inactive', 'Inactive')]

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(Inactive_Date__isnull=True)
        if self.value() == 'inactive':
            return queryset.filter(Inactive_Date__isnull=False)
        return queryset


class AnimalAdmin(admin.ModelAdmin):
    list_display = ['Name', 'Animal_Type', 'Max_Daily', 'Inactive_Date']
    list_filter = [InactiveFilter, 'Animal_Type']
    actions = ['mark_inactive', 'mark_active']

    @admin.action(description='Mark selected animals Inactive')
    def mark_inactive(self, request, queryset):
        count = queryset.update(Inactive_Date=datetime.date.today())
        self.message_user(request, f'{count} animal(s) marked inactive.')

    @admin.action(description='Mark selected animals Active')
    def mark_active(self, request, queryset):
        count = queryset.update(Inactive_Date=None)
        self.message_user(request, f'{count} animal(s) marked active.')

admin.site.register(Animal_Type)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Encounter)
