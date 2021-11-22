from django.db import models
from django.conf import settings
import datetime
from datetime import timedelta
from django.urls import reverse
from django.forms import Textarea, forms
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE



class Animal_Type(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    animal_type = models.CharField(max_length=32, unique=True)
    def __str__(self) -> str:
        return (self.animal_type)


class Animal(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    Name = models.CharField(max_length=64)
    Max_Daily = models.IntegerField(default=4)
    Inactive_Date = models.DateField(null=True, blank=True)
    Animal_Type = models.ForeignKey(Animal_Type, null=True, on_delete=models.SET_NULL, default=None)
    Comments = models.TextField(blank=True)
    def todays_encounters(self):
        theLimitDate = datetime.today() - timedelta(days=1)
        aQs = Encounter_set.filter(encounter_date__gte = theLimitDate)
        return aQs.count()
    def __str__(self) -> str:
        aStr = self.Animal_Type.__str__() + ' ' + self.Name
        return aStr
        
    class Meta:
        ordering = ['Animal_Type']

class Encounter(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE
    encounter_date = models.DateTimeField()
    animal = models.ForeignKey(Animal, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,verbose_name='Handler')
    handling_time = models.BigIntegerField(blank=True, null=True)
    crate_time = models.BigIntegerField(blank=True, null=True)
    holding_time = models.BigIntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        if self.user is None:
            aStr = 'Unknown' + '/'
        else:
             aStr = self.user.username + '/'
        if self. animal is None:
            aStr += 'Unknown'
        else:
            aStr += self.animal.Name
        return (aStr)
    
    def get_absolute_url(self):
        return reverse("encounter-detail", kwargs={"pk": self.pk})

    def get_total_minutes(self):
        #print ('self: ', self)
        if (self.handling_time < 1 and self.crate_time < 1 and self.holding_time < 1):
            theMinutes =  datetime.datetime.now() - self.encounter_date
            theMinutes = theMinutes.seconds // 60
        else:
            theMinutes = 0
            if (self.handling_time is not None):
                theMinutes += self.handling_time
            if (self.crate_time is not None):
                theMinutes += self.crate_time
            if (self.holding_time is not None):
                theMinutes += self.holding_time
        #print ('returning theMinutes:', theMinutes)
        return theMinutes


