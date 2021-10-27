from django.views.generic.list import ListView
from encounters.models import Animal, Encounter, Animal_Type
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views import generic
from django import forms
from django.http import HttpResponseRedirect
from .forms import Open_Encounter_Form, ampmDateTimeInput, encounter_update_form
from django.urls import reverse
import datetime
from datetime import date, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from django.http import JsonResponse
import csv

def index(request):
    # if not request.user.is_authenticated:
    #     return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    # else:

        num_animals = Animal.objects.all().count()
        Users = get_user_model()
        num_users = Users.objects.all().count()
        num_encounters = Encounter.objects.all().count()

        context = {
            'num_animals': num_animals,
            'num_users': num_users,
            'num_encounters': num_encounters,
        }

        return render(request, 'index.html', context = context)

@login_required
def open_encounter(request):
    if request.method == 'POST':
        #print('request: ', request.POST)
        form = Open_Encounter_Form(request.POST)
        if form.is_valid():
            #save the data
            aRecord=form.save()
            return HttpResponseRedirect(reverse('index'))
        
    else:
        current_user = request.user
        form=Open_Encounter_Form(initial={'encounter_date': datetime.datetime.today(),'user': current_user})
    return render(request, 'openencounter.html', {'form': form})

class EncountersByUserListView(LoginRequiredMixin, generic.ListView):
    model = Encounter
    template_name = 'encounters/encounters_list_by_user.html'
    
    def get_queryset(self):
        
       return Encounter.objects.filter(user=self.request.user).order_by('-encounter_date')[:10]

class AllEncountersListView(generic.ListView):
    paginate_by = 20   
    model = Encounter
    template_name = 'encounters/encounters_list_all.html'

    def get_queryset(self):
        print('in allEncounterListView, templatename: ' + self.template_name) #to prove the correct view is being called
        return Encounter.objects.all().order_by('-encounter_date')

class TodaysEncountersListView(generic.ListView):
    model = Encounter
    template_name = 'encounter_list.html'
    def get_queryset(self):
        today = datetime.datetime.now().date()
        # midnight = today.replace(hour = 0,minute = 0,second = 0)
        #print ('midnight calulated')

        return Encounter.objects.filter(encounter_date__gt = today).order_by('-encounter_date')

class AnimalTypeDetailView(generic.ListView):
    model = Animal
    fields = ['Name', 'Max_Daily','Comments']
    template_name_suffix = '_list_form'

    def get_success_url(self):
        return reverse('animaltypes')    

class EncounterDetailView(UpdateView):
    model = Encounter
    form_class = encounter_update_form
    template_name = 'encounters/encounter_update_form.html'
    extra_field = 'totalminutes'

    # cfm: the following was deprecated by front end script
    # def get_form_kwargs(self):
    #     theKwargs =  super().get_form_kwargs()
    #     theEncounter = self.get_object()
        
    #     if theEncounter.handling_time == None and theEncounter.crate_time == None and theEncounter.holding_time == None:
    #         # no times entered yet; calculate open time and put that into ht field
    #         theOpenTime =  datetime.datetime.now() - theEncounter.encounter_date
    #         theOpenTime = theOpenTime.seconds // 60
    #         theKwargs['initial'] = {'handling_time': theOpenTime}
    #     return theKwargs

    def get_success_url(self):
        return reverse('my-encounters')

class AnimalTypesListView(generic.ListView):
    model = Animal_Type
    template_name = 'encounters/animal_types_list.html'

    def get_queryset(self):
        return Animal_Type.objects.order_by('animal_type')

    
def load_animal_uses(request):
    # print('in function load_animal_uses()')
    animal_id = request.GET.get('animal')
    uses = Encounter.objects.filter(animal=animal_id, encounter_date__gte = datetime.datetime.now().date()).count()
    theMax = Animal.objects.filter(id = animal_id).values('Max_Daily')[0]['Max_Daily']
    #print (theMax)
    #uses = str(uses) + ' ( max: ' + str(theMax) + ' )'
    #cfm refine this to send both integets so that html can print in red if overused
    data = {'uses': uses, 'theMax': theMax}
    return JsonResponse(data)
    # return render(request, 'animal_uses_value.html', {'numPerDayField': uses})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('my-encounters'))

def export_data_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="EncountersData.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response

    