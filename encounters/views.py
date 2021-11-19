from django.views.generic.list import ListView
from encounters.models import Animal, Encounter, Animal_Type
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views import generic
from django import forms
from django.http import HttpResponseRedirect
from .forms import Open_Encounter_Form, encounter_update_form, export_options_form
from django.urls import reverse
import datetime
from datetime import date, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, FormView
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
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
            messages.success(request, 'Encounter saved.')
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



class EncounterDetailView(SuccessMessageMixin, UpdateView):
    model = Encounter
    form_class = encounter_update_form
    template_name = 'encounters/encounter_update_form.html'
    extra_field = 'totalminutes'
    success_message = 'Encounter updated'

    def get_success_url(self):
        return reverse('my-encounters')

class AnimalTypes(generic.ListView):
    model = Animal_Type
    template_name = 'encounters/animal_types.html'

    def get_queryset(self):
        #print (Animal_Type.objects.all().order_by('animal_type'))
        return Animal_Type.objects.all().order_by('animal_type')

def AnimalTypesDetailList(request, pk):

# look at index function for ideas

    return render(request, '.html', context = 'context')

class AnimalTypesDetailView(generic.ListView):
    model = Animal
    fields = ['Name', 'Max_Daily','Comments']
    template_name_suffix = '_list_form'

    def get_queryset(self):
        #print(self.kwargs)
        theAnimalType = self.kwargs['animal_type']
        qs = super().get_queryset().filter(Animal_Type=theAnimalType).order_by('Name')
        return qs

    def get_success_url(self):
        return reverse('animaltypes')    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theAnimalType'] = self.kwargs['animal_type']
        return context

class EncountersByAnimalListView(generic.ListView):
    model = Encounter
    fields = ['encounter_date','user','handling_time','crate_time','holding_time','comments']
    template_name_suffix = '_by_animal'

    def get_success_url(self):
        return reverse('animals')    

    def get_queryset(self):
        #print(self.kwargs)
        thePK = self.kwargs['pk']
        qs = Encounter.objects.all().filter(animal=thePK).order_by('-encounter_date')
        return qs 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thePK = self.kwargs['pk']
        #print('the pk is:', thePK)
        anAnimal = Animal.objects.filter(pk=thePK).first()
        #print ('anAnimal:', anAnimal)
        context['typeAndAnimal'] = anAnimal
        return context

def load_animal_uses(request):
    # print('in function load_animal_uses()')
    animal_id = request.GET.get('animal')
    uses = Encounter.objects.filter(animal=animal_id, encounter_date__gte = datetime.datetime.now().date()).count()
    theMax = Animal.objects.filter(id = animal_id).values('Max_Daily')[0]['Max_Daily']
    #print (theMax)
    data = {'uses': uses, 'theMax': theMax}
    return JsonResponse(data)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('my-encounters'))
    
# def login_view(request):
#     #template_name 
#     login(request)
#     return HttpResponseRedirect(reverse('todays-encounters'))

def export_data_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="EncountersData.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Date/Time', 'Animal', 'User', 'Handling Time', 'Crate Time', 'Holding time', 'Comments'])
    qs = Encounter.objects.all().order_by('-encounter_date')
    for enc in qs:
        aRow = [enc.encounter_date, enc.animal, enc.user, enc.handling_time, enc.crate_time, enc.holding_time, enc.comments]
        writer.writerow(aRow)
    return response


def export_data(request):
        if request.method == 'POST':
            form = export_options_form(request.POST)
            if form.is_valid():
                #print (form.cleaned_data)
                if form.cleaned_data['startDate'] is not None:
                    # start here and do the rest
                    print('starting qs with startdate:')
                    qs = Encounter.objects.filter(encounter_date__gte=form.cleaned_data['startDate'])
                    print(qs)
                else:
                    print('starting qs without startdate:')
                    qs = Encounter.objects.all()
                    print(qs)
                if form.cleaned_data['endDate'] is not None:
                    qs = qs.filter(encounter_date__lte=form.cleaned_data['endDate'])
                    print (qs)
                if form.cleaned_data['animals'] is not None:
                    qs = qs.filter(animal = form.cleaned_data['animals'])
                    print (qs)
                elif form.cleaned_data['animalType'] is not None:
                    print('animaltype is ')
                    print(form.cleaned_data['animalType'])
                    qs = qs.filter(animal__Animal_Type__animal_type = form.cleaned_data['animalType'])
                    print(qs)
                if form.cleaned_data['users'] is not None:
                    qs = qs.filter(user=form.cleaned_data['users'])
                    print(qs)
                # now I have the appropriate qs; download

                response = HttpResponse(
                    content_type='text/csv',
                    headers={'Content-Disposition': 'attachment; filename="EncountersData.csv"'},
                )

                writer = csv.writer(response)
                writer.writerow(['Date/Time', 'Animal', 'User', 'Handling Time', 'Crate Time', 'Holding time', 'Comments'])
                for enc in qs:
                    aRow = [enc.encounter_date, enc.animal, enc.user, enc.handling_time, enc.crate_time, enc.holding_time, enc.comments]
                    writer.writerow(aRow)
                return response


        else:
            form = export_options_form()
        return render (request, 'encounters/exportform.html', {'form':form})


def load_animals(request):
    the_animal_type_id = request.GET.get('theAnimalTypeID')
    #print('theanimaltypeid=' + the_animal_type_id)
    animals = list(Animal.objects.values('id','Name').filter(Animal_Type_id = the_animal_type_id))
    #print('in def load_animals; animals =')
    #print(animals)


    return render(request, 'encounters/animal_dropdown_list_options.html', {'animals': animals})