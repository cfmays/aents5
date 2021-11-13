from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField, TextInput, Form
from django.forms.widgets import DateTimeInput
from django.utils import timezone, formats
from encounters.models import Animal, Encounter
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django import forms
import datetime

class ampmDateTimeInput(DateTimeInput):
    def value_from_datadict(self, data, files, name):
        ACCEPTED_FORMATS = [self.format] + formats.ISO_INPUT_FORMATS['DATETIME_INPUT_FORMATS']
        orig_value = super(ampmDateTimeInput, self).value_from_datadict(data, files, name)
        value = None
        for format in ACCEPTED_FORMATS:
            try:
                value = timezone.datetime.strptime(orig_value, self.format)
            except ValueError:
                # This is not a datetime in the this format; keep going
                pass
            else:
                break
        if value is None:
            # We didn't find a format that works, pass back the original
            value = orig_value
        return value

class ampmDateTimeInput2(DateTimeInput):
    def value_from_datadict(self, data, files, name):
        #orig_value = super(ampmDateTimeInput2, self).value_from_datadict(data, files, name)
        #print (orig_value)
        # since I don't use the value of that field at all, just return something that will validate
        value = datetime.datetime.now()
        return value
        
class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses',disabled=True,required=False)

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','numPerDayField','user','handling_time','crate_time','holding_time','comments']
        widgets = {
            'handling_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'crate_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'holding_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': ampmDateTimeInput(format='%m/%d/%Y  %I:%M %p', attrs={'size': '24'}),
        }

    def __init__(self, *args, **kwargs):
        super(Open_Encounter_Form, self).__init__(*args, **kwargs)   
        self.fields['user'].queryset = User.objects.order_by('username')
        #print (User.objects)

class encounter_update_form(ModelForm):
    endTimeField = DateTimeField(label='Time returned', 
        initial=datetime.datetime.now(), 
        widget=ampmDateTimeInput2(format='%m/%d%Y  %I:%M %p', attrs={'size':'24','tabindex':50}),
        required= False)
    totalTimeField = IntegerField(label='Total Minutes', 
        widget=TextInput(attrs={'min':0,'max': '1000000','type': 'number','tabindex':51}), 
        required=False,
        disabled = True)

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','endTimeField','totalTimeField','comments']
        widgets = {
            'handling_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'crate_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'holding_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': ampmDateTimeInput(format='%m/%d/%Y  %I:%M %p', attrs={'size':'24'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(encounter_update_form, self).__init__(*args, **kwargs)   
        self.fields['user'].queryset = User.objects.order_by('username')
        #print (User.objects)

class export_options_form(Form):
    startDate = forms.DateField(label="Starting Date", required=False)
    endDate = forms.DateField(label='Ending Date', required=False)
    #animalType = forms.forms.ChoiceField('Animal Type', choices=[Animal_Type], required=False)
