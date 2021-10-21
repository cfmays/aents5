from django.db.models.fields import CharField, IntegerField, TextField
from django.forms import ModelForm, Textarea, IntegerField, CharField, DateTimeField
from django.forms.widgets import DateTimeInput
from encounters.models import Animal, Encounter
from django.views.generic.edit import UpdateView

import datetime

class ampmDateTimeInput(DateTimeInput):
    def value_from_datadict(self, data, files, name):        
        theRawDate = data['encounter_date']
        theConvertedDate = theRawDate
        # check if there is an AM or PM on the end
        if (len(theRawDate) > 2): 
            theStr = theRawDate[-2:]
            #print ('theStr: ', theStr)
            if (theStr == 'PM'):
                #convert to 24 hr format
                #get the hours
                theHrsStr = theRawDate[12:14]
                theHrs = int(theHrsStr)
                theHrs = theHrs + 12
                #pad with leading zero if needed cfm; is this EVER needed?
                theHrsStr = str(theHrs)
                if (len(theHrsStr) == 1):
                    theHrsStr = '0' + theHrsStr
                theConvertedDate = theConvertedDate[0:11] + theHrsStr + theConvertedDate[14:17]
            elif (theStr == 'AM'):
                #just strip the AM
                theConvertedDate = theConvertedDate[0:17] 
            #else just pass the existing string; the user has removed the AM or PM manually    

        # create a mutable instance of the data     
        aNewData = data.copy()
        aNewData['encounter_date'] = theConvertedDate
        return(super().value_from_datadict(aNewData, files, name))
        


class Open_Encounter_Form(ModelForm):
    numPerDayField = CharField(label='Today\'s uses')

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','numPerDayField','user','handling_time','crate_time','holding_time','comments']
        widgets = {
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': ampmDateTimeInput(format=('%m/%d/%Y  %I:%M %p'), attrs={'size':'24'}),
        }

class encounter_update_form(ModelForm):
    endTimeField = DateTimeField(label='Time returned', initial=datetime.datetime.now())

    class Meta:
        model = Encounter        
        fields = ['encounter_date','animal','user','handling_time','crate_time','holding_time','endTimeField','comments']
        widgets = {
            'comments': Textarea(attrs={'rows': 4, 'cols': 40}),
            'encounter_date': ampmDateTimeInput(format=('%m/%d/%Y  %I:%M %p'), attrs={'size':'24'}),
            'endTimeField': ampmDateTimeInput(format=('%m/%d/%Y  %I:%M %p'), attrs={'size':'24'}),
        }
