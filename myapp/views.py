from django.shortcuts import redirect, render, get_object_or_404
from .forms import newUserForm
from django.contrib.auth import authenticate,login
from django.contrib.auth.views import(
    LoginView,
    PasswordChangeView,
)
from .forms import (
    LoginForm,
    TalkForm,
    UsernameSettingForm,
    EmailSettingForm,
    ImageSettingForm,
    PasswordSettingForm,
    InquiryForm,
    FriendSearchForm,
)
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .models import Talk
from django.db.models import Q
import operator
from django.urls import reverse_lazy
from django.contrib.auth import logout
from .models import Inquiry
#from allauth.account.views import LoginView as AllauthLoginView
#from allauth.account.forms import LoginForm

def index(request):
    return render(request, "myapp/index.html")

def signup_view(request):
    if request.method == "GET":
        form = newUserForm()
        error_message = ''
    elif request.method == "POST":
        # 画像ファイルをformに入れた状態で使いたい時はformに"request.FILES"を加える。
        # request.POST だけではNoneが入る。
        form = newUserForm(request.POST, request.FILES)
        if form.is_valid():
            # モデルフォームはformの値をmodelsにそのまま格納できるsave()メソッドがあるので便利。
            form.save()
            # フォームから"username"を読み取る
            username = form.cleaned_data.get("email")
            # フォームから"password1"を読み取る
            password = form.cleaned_data.get("password1")
            # 認証情報のセットを検証するには authenticate() を利用してください。
            # このメソッドは認証情報をキーワード引数として受け取ります。
            # 検証する対象はデフォルトでは username と password であり
            # その組み合わせを個々の 認証バックエンド に対して問い合わせ、認証バックエンドで認証情報が有効とされれば
            # User オブジェクトを返します。もしいずれの認証バックエンドでも認証情報が有効と判定されなければ PermissionDenied が送出され、None が返されます。
            # (公式ドキュメントより)
            # つまり、autenticateメソッドは"username"と"password"を受け取り、その組み合わせが存在すれば
            # そのUserを返し、不正であれば"None"を返します。
            user = authenticate(username=username, password=password)
            if user is not None:
                # あるユーザーをログインさせる場合は、login() を利用してください。この関数は HttpRequest オブジェクトと User オブジェクトを受け取ります。
                # ここでのUserは認証バックエンド属性を持ってる必要がある。
                # authenticate()が返すUserはuser.backendを持つので連携可能。
                login(request, user)
            return redirect("/")
        # バリデーションが通らなかった時の処理を記述
        else:
            # エラー時 form.errors には エラー内容が格納されている
            print(form.errors)

            

    context = {
        "form": form,
    }
    return render(request, "myapp/signup.html", context)

class Login(LoginView):
    authentication_form = LoginForm
    template_name = "myapp/login.html"


def vertification(request):
    return render(request,"myapp/vertification.html")

def friends(request):
    info = []
    info_have_message = []
    info_have_no_message = []
    search_form = FriendSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data['query']
        friends = CustomUser.objects.all().exclude(username=request.user.username)
        
        if query:
            friends = friends.filter(username__icontains=query)
    else:
        friends = CustomUser.objects.all().exclude(username=request.user.username)
    for friend in friends:
        # 最新のメッセージの取得
        latest_message = Talk.objects.filter(
            Q(talk_from=request.user, talk_to=friend) | Q(talk_to=request.user, talk_from=friend)
        ).order_by('time').last()

        if latest_message:
            info_have_message.append([friend, latest_message.talk, latest_message.time])
        else:
            info_have_no_message.append([friend, None, None])
    info_have_message = sorted(info_have_message, key=operator.itemgetter(2), reverse=True)
    
    info.extend(info_have_message)
    info.extend(info_have_no_message)
    
    context = {
        "info": info,
        "search_form": search_form,
    }
    return render(request, "myapp/friends.html",context)

@login_required
def talk_room(request, user_id):
    # ユーザ・友達をともにオブジェクトで取得
    user = request.user
    friend = get_object_or_404(CustomUser, id=user_id)
    # 自分→友達、友達→自分のトークを全て取得
    talk = Talk.objects.filter(
        Q(talk_from=user, talk_to=friend) | Q(talk_to=user, talk_from=friend)
    ).order_by("time")
    # 送信form
    form = TalkForm()
    # メッセージ送信だろうが更新だろが、表示に必要なパラメーターは変わらないので、この時点でまとめて指定
    context = {
        "form": form,
        "talks": talk,
        "friend": friend,
    }

    # POST（メッセージ送信あり）
    if request.method == "POST":
        # 送信内容を取得
        new_talk = Talk(talk_from=user, talk_to=friend)
        form = TalkForm(request.POST, instance=new_talk)

        # 送信内容があった場合
        if form.is_valid():
            # 保存
            form.save()
            # 更新
            # このようなリダイレクト処理はPOSTのリクエストを初期化し、リクエストをGETに戻すことにより
            # 万一更新処理を連打されてもPOSTのままにさせない等の用途がある
            return redirect("talk_room", user_id)
        # バリデーションが通らなかった時の処理を記述
        else:
            # エラー時 form.errors には エラー内容が格納されている
            print(form.errors)

    # POSTでない（リダイレクトorただの更新）&POSTでも入力がない場合
    return render(request, "myapp/talk_room.html", context)

def setting(request):
    return render(request, "myapp/setting.html")


@login_required
def username_change(request):
    user = request.user
    if request.method == "GET":
        form = UsernameSettingForm(instance=user)

    elif request.method == "POST":
        form = UsernameSettingForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("change_done")
        # バリデーションが通らなかった時の処理を記述
        else:
            # エラー時 form.errors には エラー内容が格納されている
            print(form.errors)

    context = {
        "form": form,
    }
    return render(request, "myapp/username_change.html", context)

def change_done(request):
    return render(request,"myapp/change_done.html")

@login_required
def email_change(request):
    user = request.user
    if request.method == "GET":
        form = EmailSettingForm(instance=user)

    elif request.method == "POST":
        form = EmailSettingForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("change_done")
        # バリデーションが通らなかった時の処理を記述
        else:
            # エラー時 form.errors には エラー内容が格納されている
            print(form.errors)

    context = {
        "form": form,
    }
    return render(request, "myapp/email_change.html", context)

@login_required
def image_change(request):
    user = request.user
    if request.method=="GET":
        form = ImageSettingForm(instance=user)
    elif request.method == "POST":
        form = ImageSettingForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect("change_done")
        else:
            print(form.errors)
    context = {
        "form":form,
    }
    return render(request,"myapp/image_change.html",context)


class PasswordChange(PasswordChangeView):
    form_class = PasswordSettingForm
    success_url = reverse_lazy("change_done")
    template_name = "myapp/password_change.html"

def logout_view(request):
    logout(request)
    return render(request,"myapp/index.html")

from django.shortcuts import render, redirect
from .forms import InquiryForm

def inquiry(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            request.session['inquiry_data'] = {'name': name, 'message': message}  # セッションにデータを保存
            return redirect('inquiry_confirm')
    else:
        form = InquiryForm()

    return render(request, 'myapp/inquiry.html', {'form': form})

def inquiry_confirm(request):
    if 'inquiry_data' in request.session:
        inquiry_data = request.session['inquiry_data']
        if request.method == 'POST':
            if 'confirm' in request.POST:
                # お問い合わせ内容を保存
                Inquiry.objects.create(
                    user = request.user,
                    name=inquiry_data['name'],
                    message=inquiry_data['message']
                )
                del request.session['inquiry_data']  # セッションからデータを削除
                return redirect('inquiry_success')  # 成功ページにリダイレクト
            elif 'back' in request.POST:
                del request.session['inquiry_data']  # セッションからデータを削除
                return redirect('inquiry')  # 入力ページに戻る
        return render(request, 'myapp/inquiry_confirm.html', inquiry_data)
    else:
        return redirect('inquiry')  # セッションにデータがない場合は入力ページにリダイレクト
    
def inquiry_success(request):
    return render(request, 'myapp/inquiry_success.html')