from .models import CustomUser
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Talk
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    image = forms.ImageField(required=False)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.image = self.cleaned_data['image']
        user.save()
        return user



class TalkForm(forms.ModelForm):
    """トークの送信のためのform

    メッセージを送信するだけで、誰から誰か、時間は全て自動で対応できるのでこれだけで十分
    """

    class Meta:
        model = Talk
        fields = ("talk",)
        # 入力予測の表示をさせない（めっちゃ邪魔）
        widgets = {"talk": forms.TextInput(attrs={"autocomplete": "off"})}

class UsernameSettingForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username",)
        labels = {"labels":"新しいユーザ名"}

class EmailSettingForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = {"email",}
        labels = {"email":"新しいメールアドレス"}

class ImageSettingForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("image",)

class PasswordSettingForm(PasswordChangeForm):
    pass

class InquiryForm(forms.Form):
    name = forms.CharField(label="お名前", max_length=100)
    message = forms.CharField(label="お問い合わせ内容", widget=forms.Textarea)

class FriendSearchForm(forms.Form):
    query = forms.CharField(label='友達検索', max_length=100, required=False)