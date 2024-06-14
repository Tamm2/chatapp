from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from .forms import (
    TalkForm,
    UsernameSettingForm,
    EmailSettingForm,
    ImageSettingForm,
    PasswordSettingForm,
    InquiryForm,
    FriendSearchForm,
)
from django.contrib.auth.decorators import login_required
from .models import CustomUser,Talk,Inquiry
from django.db.models import OuterRef, Subquery, Max, Q
import operator
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.db.models.functions import Coalesce

def index(request):
    return render(request, "myapp/index.html")

@login_required
def friends(request):
    search_form = FriendSearchForm(request.GET)
    query = search_form.cleaned_data.get('query') if search_form.is_valid() else None

    friends = CustomUser.objects.exclude(username=request.user.username)
    
    if query:
        friends = friends.filter(Q(username__icontains=query) | Q(email__icontains=query))
    
    # Subquery to get the latest message for each friend
    latest_message_subquery = Talk.objects.filter(
        Q(talk_from=request.user, talk_to=OuterRef('pk')) | Q(talk_to=request.user, talk_from=OuterRef('pk'))
    ).order_by('-time').values('talk')[:1]

    # Subquery to get the latest message time for each friend
    latest_time_subquery = Talk.objects.filter(
        Q(talk_from=request.user, talk_to=OuterRef('pk')) | Q(talk_to=request.user, talk_from=OuterRef('pk'))
    ).order_by('-time').values('time')[:1]

    friends = friends.annotate(
        latest_msg_talk=Coalesce(Subquery(latest_message_subquery), None),
        latest_msg_time=Subquery(latest_time_subquery)
    ).order_by('-latest_msg_time')

    # Prepare info list for rendering
    info = []
    for friend in friends:
        if friend.latest_msg_talk:
            info.append([friend, friend.latest_msg_talk, friend.latest_msg_time])
        else:
            info.append([friend, "まだメッセージがありません", None])

    context = {
        "info": info,
        "search_form": search_form,
    }
    return render(request, "myapp/friends.html", context)


@login_required
def talk_room(request, user_id):
    # ユーザ・友達をともにオブジェクトで取得
    user = request.user
    friend = get_object_or_404(CustomUser, id=user_id)
    # 自分→友達、友達→自分のトークを全て取得
    talk = Talk.objects.select_related(
        "talk_from", "talk_to"
    ).filter(
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