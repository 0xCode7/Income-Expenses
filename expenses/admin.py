from django.contrib import admin
from .models import *


# Register your models here.

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['amount', 'category', 'description', 'owner', 'date']


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
