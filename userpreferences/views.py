import os
import json
from django.shortcuts import render
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages


# Create your views here.
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            currency_data.append({'key': key, 'value': value})

    user_exists = UserPreferences.objects.filter(user=request.user).exists()
    user_preferences = None
    if user_exists:
        user_preferences = UserPreferences.objects.get(user=request.user)

    if request.method == 'GET':
        return render(request, 'preferences/index.html',
                      {'currencies': currency_data, 'user_preferences': user_preferences})
    else:
        selected_currency = request.POST['currency']
        if user_exists:
            user_preferences.currency = selected_currency
            user_preferences.save()
        else:
            UserPreferences.objects.create(user=request.user, currency=selected_currency)
        messages.success(request, 'Changes saved successfully')

        return render(request, 'preferences/index.html',
                      {'currencies': currency_data, 'user_preferences': user_preferences})
