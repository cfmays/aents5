from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField, TextInput, Form
from django.forms.widgets import DateTimeInput
from encounters.models import Encounter, Animal_Type, Animal
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django import forms


# HTML5 datetime picker. The browser submits "YYYY-MM-DDTHH:MM", which
# Django's DateTimeField parses natively; the matching format string makes
# the initial value show up in the picker.
def datetime_local_widget(**attrs):
    attrs['type'] = 'datetime-local'
    return DateTimeInput(format='%Y-%m-%dT%H:%M', attrs=attrs)


def _bootstrap_fields(form):
    # add the Bootstrap CSS class to every widget so form.as_p looks tidy
    # (radio/checkbox groups use their own Bootstrap classes, so skip those)
    for field in form.fields.values():
        if isinstance(field.widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
            continue
        css = 'form-control'
        existing = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = (existing + ' ' + css).strip()


class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses',disabled=True,required=False)
    animalCommentsField = CharField(label='Animal comments', max_length=360, disabled=True,required=False)

    class Meta:
        model = Encounter
        fields = ['encounter_date','animal','numPerDayField','animalCommentsField','participation','user','handling_time','crate_time','holding_time','comments']
        widgets = {
            'handling_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'crate_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'holding_time': TextInput(attrs={'min':0,'max': '1000000','type': 'number'}),
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': datetime_local_widget(),
            'participation': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(Open_Encounter_Form, self).__init__(*args, **kwargs)
        # hide users whose account is marked inactive
        self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('username')
        # hide animals a supervisor has marked inactive
        self.fields['animal'].queryset = Animal.objects.filter(Inactive_Date__isnull=True)
        self.fields['participation'].initial = None
        _bootstrap_fields(self)

class encounter_update_form(ModelForm):
    endTimeField = DateTimeField(label='Time returned',
        widget=datetime_local_widget(tabindex=50),
        required=False)  # display helper only; the JavaScript keeps it in sync
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
            'encounter_date': datetime_local_widget(),
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
