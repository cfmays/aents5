from django.forms import ModelForm, Textarea
from encounters.models import Animal, Encounter
import datetime

class Open_Encounter_Form(ModelForm):
    #extra_field = forms.IntegerField()
    class Meta:
        model = Encounter
        # cfm: following widget adjustment does not work?
        widgets = {
            'comments': Textarea(attrs={'rows': 4, 'cols': 40})
        }
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','comments']



class old_Open_Encounter_Form(ModelForm):
    #extra_field = forms.IntegerField()
    class Meta:
        model = Encounter
        # cfm: following widget adjustment does not work?
        widgets = {
            'Comments': Textarea(attrs={'rows': 6, 'cols': 43})
        }
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','comments']

