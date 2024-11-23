import json
from lib2to3.fixes.fix_input import context

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import auth
from .utils import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading


# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


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

                email = EmailMessage(
                    email_subject,
                    email_body,
                    None,
                    [email],
                )

                EmailThread(email).start()
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


class ResetPasswordView(View):

    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
            'data': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            return render(request, 'authentication/reset-password.html', context)

        user = User.objects.filter(email=email)
        if user.exists():
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].id))
            link = reverse('reset-user-password',
                           kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user[0])})
            activation_url = 'http://' + domain + link

            email_subject = 'Password reset instructions'
            email_body = 'Hi ' + user[0].username + ' click the link below to reset your password \n' + activation_url

            email = EmailMessage(
                email_subject,
                email_body,
                None,
                [email],
            )

            EmailThread(email).start()
            messages.success(request, 'We have sent you a link to reset your password')
        else:
            messages.error(request, 'Email does not exist')

        return render(request, 'authentication/reset-password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.info(request, 'Password link is invalid, please request a new one')
            return render(request, 'authentication/reset-password.html')

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful, you can now login with your new password')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Something went wrong')
            return render(request, 'authentication/set-new-password.html', context)
    #
    # return render(request, 'authentication/set-new-password.html')


class ProfileView(View):
    def get(self, request):
        context = {
            'user': request.user
        }
        return render(request, 'authentication/profile.html', context)

    def post(self, request):
        user = request.user
        user_data = User.objects.get(id=user.id)

        username = request.POST['username']
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username is already in use, choose another one')
            return render(request, 'authentication/profile.html')

        email = request.POST['email']
        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            return redirect('profile')

        user_data.username = request.POST['username']
        user_data.email = request.POST['email']

        if request.POST['password']:
            password = request.POST['password']
            if len(password) < 6:
                messages.error(request, 'Password too short')
                return redirect('profile')
            user_data.set_password(password)
            update_session_auth_hash(request, user_data) # prevent Logout after Password change
        user_data.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
