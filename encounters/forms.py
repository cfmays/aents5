from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField
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
        }


class old_Open_Encounter_Form(ModelForm):
    #extra_field = forms.IntegerField()
    class Meta:
        model = Encounter
        # cfm: following widget adjustment does not work?
        widgets = {
            'Comments': Textarea(attrs={'rows': 6, 'cols': 43})
        }
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','comments']

