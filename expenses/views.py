from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

from userpreferences.models import UserPreferences
from .models import *
import json


# Create your views here.

def handle_expanse_form(request, expense=None, template_name='expenses/add-expense.html'):
    categories = Category.objects.all()
    context = {"categories": categories}

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        category_id = request.POST['category']
        date = request.POST['expense_date']

        if not amount:
            messages.error(request, 'Amount is required')
            context = {"values": ىيثءrequest.POST, "categories": categories}
            return render(request, 'expenses/add-expense.html', context)
        if not description:
            messages.error(request, 'Description is required')
            context = {"values": request.POST, "categories": categories}
            return render(request, 'expenses/add-expense.html', context)
        category = Category.objects.get(id=category_id)

        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = now().date()  # Default to today's date

        # For updating an expense
        if expense:
            expense.amount = amount
            expense.description = description
            expense.category = category
            expense.date = date
            expense.save()
            messages.success(request, 'Expense updated successfully')
        else:
            expense = Expense.objects.create(
                amount=amount,
                description=description,
                category=category,
                date=date,
                owner=request.user
            )
            expense.save()
            messages.success(request, 'Expense added successfully')
        return redirect('expenses')
    if expense:
        context['expense'] = expense
    return render(request, template_name, context)


def search_expenses(request):
    if request.method == 'POST':
        try:
            search_str = json.loads(request.body).get('searchText')
            expenses = (Expense.objects.filter(amount__istartswith=search_str, owner=request.user) |
                        Expense.objects.filter(date__istartswith=search_str, owner=request.user) |
                        Expense.objects.filter(description__icontains=search_str, owner=request.user) |
                        Expense.objects.filter(category__name__icontains=search_str, owner=request.user))
            data = [
                {
                    'id': expense.id,
                    'amount': expense.amount,
                    'description': expense.description,
                    'category': expense.category.name,  # Include related field's name
                    'date': str(expense.date)  # Convert date to string for JSON serialization
                }
                for expense in expenses
            ]
            return JsonResponse(list(data), safe=False)
        except Exception as e:
            print(f"Error in search_expenses: {e}")  # Log the error
            return JsonResponse({'error': 'Something went wrong'}, status=500)


@login_required(login_url='/auth/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    currency = UserPreferences.objects.get(user=request.user).currency

    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {"categories": categories, "expenses": expenses, "page_obj": page_obj}
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/auth/login')
def add_expense(request):
    return handle_expanse_form(request)


@login_required(login_url='/auth/login')
def update_expense(request, id):
    expense = get_object_or_404(Expense, pk=id)
    return handle_expanse_form(request, expense, template_name='expenses/update-expense.html')


@login_required(login_url='/auth/login')
def delete_expense(request, id):
    if request.method != 'POST':
        expense = Expense.objects.get(pk=id)
        expense.delete()
        messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')
