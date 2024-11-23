from datetime import date, timedelta
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreferences
from .models import *
import json
import csv


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
            context = {"values": request.POST, "categories": categories}
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

    context = {"categories": categories, "expenses": expenses, "page_obj": page_obj, "currency": currency}
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


@login_required(login_url='/auth/login')
def expense_summary(request):
    today_date = date.today()
    six_months_ago = today_date - timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=today_date)
    final = {}

    def get_category(expense):
        return expense.category

    def get_expense_category_amount(category):
        items = Expense.objects.filter(category=category)
        amount = sum(item.amount for item in items)
        return amount

    category_list = list(set(map(get_category, expenses)))
    for expense in expenses:
        for category in category_list:
            final[str(category)] = get_expense_category_amount(category)

    return JsonResponse({'category_data': final}, safe=False)


def stats(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(now()) + '.csv'
    expenses = Expense.objects.filter(owner=request.user)
    currency = UserPreferences.objects.get(user=request.user).currency
    print(currency)
    writer = csv.writer(response)
    writer.writerow(['Amount  (' + str(currency[:3]) + ')', 'Category', 'Description', 'Date'])
    for expense in expenses:
        writer.writerow([expense.amount, expense.category, expense.description, expense.date])
    return response

