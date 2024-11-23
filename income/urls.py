from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.index, name='incomes'),
    path('search/', views.search_incomes, name='search-incomes'),
    path('add-income/', views.add_income, name='add-income'),
    path('update-income/<int:id>', views.update_income, name='update-income'),
    path('delete-income/<int:id>', views.delete_income, name='delete-income'),

]
