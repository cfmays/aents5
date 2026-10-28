from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
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
        theLimitDate = datetime.datetime.today() - timedelta(days=1)
        # count encounters as the main animal or as the companion
        aQs = Encounter.objects.filter(Q(animal=self) | Q(companion=self), encounter_date__gte = theLimitDate)
        return aQs.count()
    def __str__(self) -> str:
        aStr = self.Animal_Type.__str__() + ' ' + self.Name
        return aStr
        
    class Meta:
        ordering = ['Animal_Type']

class Encounter(SafeDeleteModel):
    PARTICIPATED = 'participated'
    REFUSED = 'refused'  # stored value kept as 'refused' so older records still match
    REFUSED_PROGRAM = 'refused_program'
    PARTICIPATION_CHOICES = [
        (PARTICIPATED, 'Participated'),
        (REFUSED, 'Refused at the start'),
        (REFUSED_PROGRAM, 'Refused at the program'),
    ]

    _safedelete_policy = SOFT_DELETE
    encounter_date = models.DateTimeField()
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    companion = models.ForeignKey(Animal, on_delete=models.PROTECT, null=True, blank=True,
        related_name='companion_encounters')
    # 'user' is the Retrieval handler (field name kept from when there was only one handler)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Retrieval Handler')
    presentation_handler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name='presentation_encounters', verbose_name='Presentation Handler')
    return_handler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name='return_encounters', verbose_name='Return Handler')
    participation = models.CharField(max_length=16, choices=PARTICIPATION_CHOICES, default=PARTICIPATED)
    handling_time = models.BigIntegerField(blank=True, null=True)
    crate_time = models.BigIntegerField(blank=True, null=True)
    holding_time = models.BigIntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.user.username + '/' + self.animal.Name
    
    def clean(self):
        if self.companion_id and self.companion_id == self.animal_id:
            raise ValidationError({'companion': 'The companion must be a different animal.'})

    def get_absolute_url(self):
        return reverse("encounter-detail", kwargs={"pk": self.pk})

    @property
    def is_open(self):
        # no time logged yet means the animal is still out
        return not (self.handling_time or self.crate_time or self.holding_time)

    def get_total_minutes(self):
        handling_time = self.handling_time or 0
        crate_time = self.crate_time or 0
        holding_time = self.holding_time or 0
        if (handling_time < 1 and crate_time < 1 and holding_time < 1):
            theMinutes = datetime.datetime.now() - self.encounter_date
            theMinutes = theMinutes.seconds // 60
        else:
            theMinutes = handling_time + crate_time + holding_time
        return theMinutes




class AnnouncementSeen(models.Model):
    # one row per user per announcement they have already been shown
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    announcement = models.CharField(max_length=64)

    class Meta:
        unique_together = ['user', 'announcement']
