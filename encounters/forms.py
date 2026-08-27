from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField, TextInput, Form
from django.forms.widgets import DateTimeInput
from django.utils import timezone, formats
from encounters.models import Encounter, Animal_Type, Animal
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django import forms
import datetime

class ampmDateTimeInput(DateTimeInput):
    def value_from_datadict(self, data, files, name):
        ACCEPTED_FORMATS = [self.format] + formats.ISO_INPUT_FORMATS['DATETIME_INPUT_FORMATS']
        orig_value = super(ampmDateTimeInput, self).value_from_datadict(data, files, name)
        if orig_value is None:
            return None
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
        
def _bootstrap_fields(form):
    # add the Bootstrap CSS class to every widget so form.as_p looks tidy
    for field in form.fields.values():
        css = 'form-control'
        existing = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = (existing + ' ' + css).strip()


class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses',disabled=True,required=False)
    animalCommentsField = CharField(label='Animal comments', max_length=360, disabled=True,required=False)

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','numPerDayField','animalCommentsField','user','handling_time','crate_time','holding_time','comments']
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
        _bootstrap_fields(self)

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
        _bootstrap_fields(self)

class export_options_form(Form):
    startDate = forms.DateField(label="Starting Date", required=False)
    endDate = forms.DateField(label='Ending Date', required=False)
    animalType = forms.ModelChoiceField(label='Animal Type', queryset=Animal_Type.objects.all(), required=False)
    animals = forms.ModelChoiceField(label='Single Animal', queryset=Animal.objects.all(), required=False)
    users = forms.ModelChoiceField(label='Handler', queryset=User.objects.order_by('username'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_fields(self)
