from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField, TextInput
from django.forms.widgets import DateTimeInput
from django.utils import timezone, formats
from encounters.models import Animal, Encounter
from django.views.generic.edit import UpdateView

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
        
class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses',disabled=True)

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

class encounter_update_form(ModelForm):
    endTimeField = DateTimeField(label='Time returned', initial=datetime.datetime.now(), widget=ampmDateTimeInput(format='%m/%Y  %I:%M %p', attrs={'size':'24'}))

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','endTimeField','comments']
        widgets = {
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': ampmDateTimeInput(format='%m/%d/%Y  %I:%M %p', attrs={'size':'24'}),
        }
