from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django import forms
from chat import models
from chat.utils.pwd_encrypt import hash_password, verify_password
from chat.utils.secret_key_generator import generate_key
from chat.utils.msgEncryptAndDecrypt import msg_decrypt


# Create your views here.

def login(request):
    if request.method == 'POST':
        data = request.POST
        # print(data)
        usr = models.User.objects.filter(username=data.get('username')).first()
        if usr and verify_password(data.get('password'), usr.password):
            request.session['user'] = {'id': usr.id, 'username': usr.username}
            return redirect('chat')
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误'})
    else:
        return render(request, 'login.html')


class RegisterModelForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['username', 'password', 'email']
        widgets = {
            'username': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'password': forms.widgets.PasswordInput(attrs={'class': 'form-control'}),
            'email': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return hash_password(pwd)


def register(request):
    if request.method == 'POST':
        form = RegisterModelForm(data=request.POST)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'register.html', {'form': form})

    else:
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})


def chat(request):
    user = request.session.get('user').get('username')
    friends = models.SecretKey.objects.filter(user=models.User.objects.filter(username=user).first())
    return render(request, 'chat.html', {'friends': friends})


def test(request):
    return redirect('chat')


def key(request):
    keys = models.SecretKey.objects.filter(
        user=models.User.objects.filter(username=request.session.get('user').get('username')).first())
    return render(request, 'key.html', {'keys': keys})


def logout(request):
    request.session.clear()
    return redirect('login')


def create_key(request):
    if request.method == 'POST':
        obj = request.POST.get('username')
        remark = request.POST.get('remark')
        user = request.session.get('user').get('username')
        # print(obj, remark, user)
        if not models.User.objects.filter(username=obj).exists():
            return JsonResponse({'status': False, 'msg': '用户不存在'})
        elif obj == user:
            return JsonResponse({'status': False, 'msg': '不能创建自己的密钥'})
        elif models.SecretKey.objects.filter(user=models.User.objects.filter(username=user).first(),
                                             obj=models.User.objects.filter(username=obj).first()).exists():
            return JsonResponse({'status': False, 'msg': '已存在密钥'})
        else:
            models.Application.objects.update_or_create(obj=models.User.objects.filter(username=obj).first(),
                                                        user=models.User.objects.filter(username=user).first(),
                                                        defaults={
                                                            'remark': remark,
                                                            'create_time': timezone.now(),
                                                            'status': '0'}
                                                        )
            return JsonResponse({'status': True, 'msg': '创建成功'})


def get_app(request):
    user = request.session.get('user').get('username')
    apps = models.Application.objects.filter(obj=models.User.objects.filter(username=user).first())
    app_array = [{'username': app.user.username, 'remark': app.remark} for app in apps if app.status == 0]
    return JsonResponse({'status': True, 'data': app_array})


def accept_app(request):
    obj_name = request.GET.get('username')
    user_name = request.session.get('user').get('username')
    # print(obj_name, user_name)
    # print(generate_key(32))
    secret_key = generate_key(32)
    models.SecretKey.objects.create(user=models.User.objects.filter(username=user_name).first(),
                                    obj=models.User.objects.filter(username=obj_name).first(), key=secret_key)
    models.SecretKey.objects.create(user=models.User.objects.filter(username=obj_name).first(),
                                    obj=models.User.objects.filter(username=user_name).first(), key=secret_key)
    models.Application.objects.filter(user=models.User.objects.filter(username=obj_name).first(),
                                      obj=models.User.objects.filter(username=user_name).first()).update(status=1)
    return JsonResponse({'status': True, 'msg': '创建成功'})


def reject_app(request):
    obj_name = request.GET.get('username')
    user_name = request.session.get('user').get('username')
    models.Application.objects.filter(user=models.User.objects.filter(username=obj_name).first(),
                                      obj=models.User.objects.filter(username=user_name).first()).update(status=2)
    return JsonResponse({'status': True, 'msg': '已拒绝'})


def check_key(request):
    obj_id = request.GET.get('userid')
    user_name = request.session.get('user').get('username')
    secret_key = request.GET.get('key')
    if models.SecretKey.objects.filter(user=models.User.objects.filter(username=user_name).first(),
                                       obj=models.User.objects.filter(id=obj_id).first(), key=secret_key).exists():
        return JsonResponse({'status': True, 'msg': 'success'})
    else:
        return JsonResponse({'status': False, 'msg': '密钥不正确'})


def load_msg(request):
    user = request.session.get('user').get('username')
    obj = request.GET.get('obj_id')
    query_1 = models.Message.objects.filter(sender__username=user, receiver_id__exact=obj)
    query_2 = models.Message.objects.filter(receiver__username=user, sender_id__exact=obj)
    messages = query_1.union(query_2).order_by('create_time')
    key = models.SecretKey.objects.filter(user__username=user, obj_id=obj).first().key
    for msg in messages:
        msg.content = msg_decrypt(msg.content, key)
    msg_array = [{'sender': msg.sender.username, 'content': msg.content, 'time': msg.create_time} for msg in messages]
    return JsonResponse({'status': True, 'data': msg_array})


def get_id(request):
    # print(request.session.get('user').get('id'))
    return JsonResponse({'status': True, 'data': request.session.get('user').get('id')})
