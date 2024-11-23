from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Income(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, blank=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.source.name) + ': ' + str(self.description)

    class Meta:
        ordering = ['-date']
