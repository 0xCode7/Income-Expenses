from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['-date']
