from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField
from django.forms.widgets import DateTimeInput
from encounters.models import Animal, Encounter
import datetime

class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses')
    #aNumField = CharField(name='Today',max_length=4)

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','numPerDayField','user','handling_time','crate_time','holding_time','comments']
        widgets = {
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            #cfm following displays correctly, but does not validate
            #'encounter_date': DateTimeInput(format=('%m/%d/%Y  %I:%M:%S %p'), attrs={'size':'24'}),
            'encounter_date': DateTimeInput(format=('%m/%d/%Y  %H:%M'), attrs={'size':'24'}),
        }


class old_Open_Encounter_Form(ModelForm):
    #extra_field = forms.IntegerField()
    class Meta:
        model = Encounter
        widgets = {
            'Comments': Textarea(attrs={'rows': 6, 'cols': 43})
        }
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','comments']

