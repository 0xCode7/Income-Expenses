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

def handle_expanse_form(request, income=None, template_name='income/add-income.html'):
    sources = Source.objects.all()
    context = {"sources": sources}

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        source_id = request.POST['source']
        date = request.POST['income_date']

        if not amount:
            messages.error(request, 'Amount is required')
            context = {"values": request.POST, "sources": sources}
            return render(request, 'income/add-income.html', context)
        if not description:
            messages.error(request, 'Description is required')
            context = {"values": request.POST, "sources": sources}
            return render(request, 'income/add-income.html', context)
        source = Source.objects.get(id=source_id)

        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = now().date()  # Default to today's date

        # For updating an income
        if income:
            income.amount = amount
            income.description = description
            income.source = source
            income.date = date
            income.save()
            messages.success(request, 'Income updated successfully')
        else:
            # For adding a new income
            income = Income.objects.create(
                amount=amount,
                description=description,
                source=source,
                date=date,
                owner=request.user
            )
            income.save()
            messages.success(request, 'Income added successfully')
        return redirect('incomes')
    if income:
        context['income'] = income
    return render(request, template_name, context)


def search_incomes(request):
    if request.method == 'POST':
        try:
            search_str = json.loads(request.body).get('searchText')
            incomes = (Income.objects.filter(amount__istartswith=search_str, owner=request.user) |
                        Income.objects.filter(date__istartswith=search_str, owner=request.user) |
                        Income.objects.filter(description__icontains=search_str, owner=request.user) |
                        Income.objects.filter(source__name__icontains=search_str, owner=request.user))
            data = [
                {
                    'id': income.id,
                    'amount': income.amount,
                    'description': income.description,
                    'source': income.source.name,  # Include related field's name
                    'date': str(income.date)  # Convert date to string for JSON serialization
                }
                for income in incomes
            ]
            return JsonResponse(list(data), safe=False)
        except Exception as e:
            print(f"Error in search_incomes: {e}")  # Log the error
            return JsonResponse({'error': 'Something went wrong'}, status=500)


@login_required(login_url='/auth/login')
def index(request):
    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user)
    currency = UserPreferences.objects.get(user=request.user).currency

    paginator = Paginator(incomes, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    context = {"sources": sources, "incomes": incomes, "page_obj": page_obj, "currency": currency}
    return render(request, 'income/index.html', context)


@login_required(login_url='/auth/login')
def add_income(request):
    return handle_expanse_form(request)


@login_required(login_url='/auth/login')
def update_income(request, id):
    income = get_object_or_404(Income, pk=id)
    return handle_expanse_form(request, income, template_name='income/update-income.html')


@login_required(login_url='/auth/login')
def delete_income(request, id):
    if request.method != 'POST':
        income = Income.objects.get(pk=id)
        income.delete()
        messages.success(request, 'Income deleted successfully')
    return redirect('incomes')


@login_required(login_url='/auth/login')
def income_summary(request):
    today_date = date.today()
    six_months_ago = today_date - timedelta(days=30 * 6)
    incomes = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=today_date)
    final = {}

    def get_source(income):
        return income.source.name

    def get_income_source_amount(source):
        items = Income.objects.filter(source=source)
        amount = sum(item.amount for item in items)

        return amount

    source_list = list(set(map(get_source, incomes)))
    for income in incomes:
        final[str(income)] = get_income_source_amount(income)

    return JsonResponse({'source_data': final}, safe=False)


def stats(request):
    return render(request, 'income/state.html')