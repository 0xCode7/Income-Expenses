from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
    path('income/', include('income.urls')),
    path('auth/', include('authentication.urls')),

    path('preferences/', include('userpreferences.urls'))
]
