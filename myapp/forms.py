from .models import CustomUser
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from .models import Talk
from django.contrib.auth import get_user_model

class newUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username","email","image")
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています。')
        return email

class LoginForm(AuthenticationForm):
    otp_code = forms.CharField(label="OTP Code", required=False)
    def clean(self):
        cleaned_data = super().clean()
        # OTPの検証ロジックをここに追加
        return cleaned_data


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