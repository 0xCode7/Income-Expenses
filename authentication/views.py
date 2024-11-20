import json
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import auth
from .utils import account_activation_token


# Create your views here.
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"username_error": 'sorry username in use, choose another one'}, status=400)

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if User.objects.filter(email=email):
            return JsonResponse({"email_error": 'Email is already in use, choose another one'}, status=400)

        return JsonResponse({'email_valid': True})


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('expenses')
        return render(request, 'authentication/register.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('expenses')

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'field_values': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html')
                user = User.objects.create_user(username=username, email=email, password=password)

                # This is the code that sends the email to the user
                user.is_active = False
                domain = get_current_site(request).domain
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                link = reverse('activate',
                               kwargs={'uidb64': uidb64, 'token': account_activation_token.make_token(user)})
                activation_url = 'http://' + domain + link

                email_subject = 'Activate your account'
                email_body = 'Hi ' + user.username + ' Please use this link to verify your account\n' + activation_url

                send_mail(
                    email_subject,
                    email_body,
                    'noreply@0xCode.com',
                    [email],
                    fail_silently=False,
                )
                user.save()
                messages.info(request, 'Please check your email to verify your account')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not account_activation_token.check_token(user, token):
                messages.error(request, "Account already activated")
                return redirect('login')

            if user.is_active:
                return redirect('login')

            user.is_active = True
            user.save()
            messages.success(request, "Account Activated Successfully")

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('expenses')
        return render(request, 'authentication/login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('expenses')

        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' + user.username + '. You are now logged in')
                    return redirect('expenses')
                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
