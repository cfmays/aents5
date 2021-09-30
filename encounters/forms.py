from django.forms import ModelForm, Textarea
from encounters.models import Animal, Encounter
import datetime

class Open_Encounter_Form(ModelForm):
    #extra_field = forms.IntegerField()
    class Meta:
        model = Encounter
        # cfm: following widget adjustment does not work?
        widgets = {
            'Comments': Textarea(attrs={'rows': 6, 'cols': 43})
        }
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','comments']

        # def __init__(self, *args, **kwargs):
        #     super(Encounter, self).__init__(*args, **kwargs)
        #     self.fields['animal'].choices = ['achoicd'] + list(Animal.objects.all().values_list('id', 'Name').order_by('Name'))
