import string
import random
import time
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail

from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('form', reverse('home')))
    else:
        login_form = LoginForm()

    context = {'login_form': login_form}
    return render(request, 'login.html', context)


def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 或者实例化
            # user = User()
            # user.username = username
            # user.email = email
            # user.set_password(password)
            # user.save()

            # 清楚session
            del request.session['register_code']

            # 用户登录
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('form', reverse('home')))

    else:
        reg_form = RegForm()
    context = {'reg_form': reg_form}
    return render(request, 'register.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)


def change_nickname(request):
    redirect_to = request.GET.get('form', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {'page_title': '修改昵称', 'form_title': '修改昵称', 'submit_text': '修改',
               'form': form, 'return_back_url': redirect_to}
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('form', reverse('home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {'page_title': '绑定邮箱', 'form_title': '绑定邮箱', 'submit_text': '绑定',
               'form': form, 'return_back_url': redirect_to}
    return render(request, 'bind_email.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if (now - send_code_time) < 30:
            data['status'] = 'ERROR'
        else:
            # 发送邮件
            request.session[send_for] = code
            request.session['send_code_time'] = now
            send_mail('绑定邮箱', '验证码:%s' % code, '951416267@qq.com', [email], fail_silently=False, )

            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

            # 不能直接赋值，否则无加密
            user.set_password(new_password)
            user.save()
            # 退出登录，返回首页
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()
    context = {'page_title': '修改密码', 'form_title': '修改密码', 'submit_text': '修改',
               'form': form, 'return_back_url': redirect_to}
    return render(request, 'form.html', context)


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)

            # 不能直接赋值，否则无加密
            user.set_password(new_password)
            user.save()
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()
    context = {'page_title': '重置密码', 'form_title': '重置密码', 'submit_text': '重置',
               'form': form, 'return_back_url': redirect_to}
    return render(request, 'forgot_password.html', context)
