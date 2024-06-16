import os

from PIL import Image
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from typing import Iterator

from django.core.files import File
from django.core.files.base import ContentFile

from accounts.models import User, SiggAreas, Profile
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# class SignupForm(UserCreationForm):
#     user_no = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
#     username = forms.CharField(max_length=20, required=True)
#     email = forms.EmailField(required=True, max_length=45)
#     birthday = forms.DateField(
#         required=True, widget=forms.DateInput(attrs={"type": "date"})
#     )
#     gender = forms.ChoiceField(choices=Authentication.GENDER_CHOICES, required=True)
#     cell_phone = forms.CharField(max_length=20, required=True)
#
#     # Additional fields for player profile
#     sido_name = forms.ModelChoiceField(
#         queryset=SiggAreas.objects.values_list("sido_name", flat=True).distinct(),
#         required=True,
#         empty_label="Select City",
#     )
#     sigg_name = forms.ModelChoiceField(
#         queryset=SiggAreas.objects.none(),  # 초기값은 비워둠
#         required=True,
#         empty_label="Select District",
#     )
#     position_1 = forms.ChoiceField(
#         choices=[
#             ("공격", "공격"),
#             ("미드", "미드"),
#             ("수비", "수비"),
#             ("골키퍼", "골키퍼"),
#         ],
#         required=True,
#         widget=forms.RadioSelect,
#     )
#     ability_1 = forms.ChoiceField(
#         choices=[
#             ("슛", "슛"),
#             ("패스", "패스"),
#             ("드리블", "드리블"),
#             ("체력", "체력"),
#             ("스피드", "스피드"),
#             ("피지컬", "피지컬"),
#         ],
#         required=True,
#         widget=forms.RadioSelect,
#     )
#     level = forms.IntegerField(min_value=1, max_value=5, required=True)
#
#     class Meta(UserCreationForm.Meta):
#         model = Authentication
#         fields = [
#             "user_no",
#             "username",
#             "password1",
#             "password2",
#             "email",
#             "birthday",
#             "gender",
#             "cell_phone",
#             "sido_name",
#             "sigg_name",
#             "position_1",
#             "ability_1",
#             "level",
#         ]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if "sido_name" in self.data:
#             try:
#                 city = self.data.get("sido_name")
#                 self.fields["sigg_name"].queryset = SiggAreas.objects.filter(
#                     sido_name=city
#                 ).values_list("sigg_name", flat=True)
#             except (ValueError, TypeError):
#                 pass  # invalid input from the client; ignore and fallback to empty district queryset
#         else:
#             self.fields["sigg_name"].queryset = SiggAreas.objects.none()
#
#         # 이메일 주소 필수필드로 만들기
#         self.fields["email"].required = True
#
#         self.helper = FormHelper()
#         self.helper.attrs = {"novalidate": True}
#         self.helper.layout = Layout(
#             "user_no",
#             "username",
#             "password1",
#             "password2",
#             "email",
#             "birthday",
#             "gender",
#             "cell_phone",
#             "sido_name",
#             "sigg_name",
#             "position_1",
#             "ability_1",
#             "level",
#             HTML("<h2>플레이어 포지션</h2>"),
#             Field("position_1", template="accounts/custom_radio.html"),
#             HTML("<h2>자신있는 능력</h2>"),
#             Field("ability_1", template="accounts/custom_radio.html"),
#             HTML("<hr>"),
#             HTML("<h2>축구 수준</h2>"),
#             Field("level", template="accounts/custom_slider.html"),
#             Submit("submit", "회원가입", css_class="w-100"),
#         )
#
#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if email:
#             user_qs = Authentication.objects.filter(email__iexact=email)
#             if user_qs.exists():
#                 raise ValidationError("이미 등록된 이메일 주소입니다.")
#         return email


class SignupForm(UserCreationForm):
    user_id = forms.CharField(max_length=20, required=True)
    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True, max_length=45)
    birth_date = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True)
    cellphone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "예)01012341234"}),
    )
    sido_name = forms.ChoiceField(
        choices=[
            (sido, sido)
            for sido in SiggAreas.objects.values_list("sido_name", flat=True).distinct()
        ],
        required=True,
        label="도시",
    )
    sigg_name = forms.ChoiceField(
        choices=[(sigg.sigg_name, sigg.sigg_name) for sigg in SiggAreas.objects.all()],
        required=True,
        label="지역구",
    )
    nickname = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "최대 10자"}),
    )
    position_1 = forms.ChoiceField(
        choices=[
            ("공격", "공격"),
            ("미드", "미드"),
            ("수비", "수비"),
            ("골키퍼", "골키퍼"),
        ],
        required=True,
        widget=forms.RadioSelect,
    )
    ability_1 = forms.ChoiceField(
        choices=[
            ("슛", "슛"),
            ("패스", "패스"),
            ("드리블", "드리블"),
            ("체력", "체력"),
            ("스피드", "스피드"),
            ("피지컬", "피지컬"),
        ],
        required=True,
        widget=forms.RadioSelect,
    )
    level = forms.IntegerField(min_value=1, max_value=5, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "user_id",
            "username",
            "password1",
            "password2",
            "email",
            "birth_date",
            "gender",
            "cellphone",
            "sido_name",
            "sigg_name",
            "nickname",
            "position_1",
            "ability_1",
            "level",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            "user_id",
            "username",
            "password1",
            "password2",
            "email",
            "birth_date",
            "gender",
            "cellphone",
            "sido_name",
            "sigg_name",
            "nickname",
            HTML("<h2>플레이어 포지션</h2>"),
            Field("position_1", template="accounts/custom_radio.html"),
            HTML("<h2>자신있는 능력</h2>"),
            Field("ability_1", template="accounts/custom_radio.html"),
            HTML("<hr>"),
            HTML("<h2>축구 수준</h2>"),
            Field("level", template="accounts/custom_slider.html"),
            Submit("submit", "회원가입", css_class="w-100"),
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            user_qs = User.objects.filter(email__iexact=email)
            if user_qs.exists():
                raise ValidationError("이미 등록된 이메일 주소입니다.")
        return email


class EditProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True)
    nickname = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "최대 10자"}),
    )
    sido_name = forms.ChoiceField(
        choices=[
            (sido, sido)
            for sido in SiggAreas.objects.values_list("sido_name", flat=True).distinct()
        ],
        required=True,
        label="City",
    )
    sigg_name = forms.ChoiceField(
        choices=[(sigg.sigg_name, sigg.sigg_name) for sigg in SiggAreas.objects.all()],
        required=True,
        label="District",
    )
    introduction = forms.CharField(
        max_length=55,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "최대 55자", "style": "width: 100%;"}
        ),
    )
    position_1 = forms.ChoiceField(
        choices=[
            ("공격", "공격"),
            ("미드", "미드"),
            ("수비", "수비"),
            ("골키퍼", "골키퍼"),
        ],
        required=True,
        widget=forms.RadioSelect,
        label="주 포지션",
    )
    ability_1 = forms.ChoiceField(
        choices=[
            ("슛", "슛"),
            ("패스", "패스"),
            ("드리블", "드리블"),
            ("체력", "체력"),
            ("스피드", "스피드"),
            ("피지컬", "피지컬"),
        ],
        required=True,
        widget=forms.RadioSelect,
        label="자신있는 능력",
    )
    level = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={"type": "range", "min": "1", "max": "5"}),
        label="축구 수준",
    )

    class Meta:
        model = User
        fields = [
            "image_url",
            "username",
            "nickname",
            "sido_name",
            "sigg_name",
            "introduction",
            "position_1",
            "ability_1",
            "level",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {"novalidate": True}
        self.helper.layout = Layout(
            "image_url",
            "username",
            "nickname",
            "sido_name",
            "sigg_name",
            "introduction",
            HTML("<h2>주 포지션</h2>"),
            Field("position_1", template="accounts/custom_radio.html"),
            HTML("<h2>자신있는 능력</h2>"),
            Field("ability_1", template="accounts/custom_radio.html"),
            HTML("<hr>"),
            HTML("<h2>축구 수준</h2>"),
            Field("level", template="accounts/custom_slider.html"),
            Submit("submit", "저장", css_class="w-100"),
        )

    def clean_avatar(self):
        avatar_file: File = self.cleaned_data.get("image_url")
        if avatar_file:
            img = Image.open(avatar_file)
            MAX_SIZE = (512, 512)
            img.thumbnail(MAX_SIZE)
            img = img.convert("RGB")

            thumb_name = os.path.splitext(avatar_file.name)[0] + ".jpg"

            thumb_file = ContentFile(b"", name=thumb_name)
            img.save(thumb_file, format="jpeg")

            return thumb_file

        return avatar_file


class LoginForm(AuthenticationForm):
    helper = FormHelper()
    helper.attrs = {"novalidate": True}
    helper.layout = Layout("username", "password")
    helper.add_input(Submit("submit", "로그인", css_class="w-100"))


from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="기존 비밀번호",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "기존 비밀번호"}
        ),
    )
    new_password1 = forms.CharField(
        label="새 비밀번호",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "새 비밀번호"}
        ),
    )
    new_password2 = forms.CharField(
        label="새 비밀번호 확인",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "새 비밀번호 확인"}
        ),
    )


token_generator = default_token_generator


class PasswordResetForm(forms.Form):
    # 이메일 포맷에 대한 유효성 검사만 수행할 뿐, 이메일의 존재 유무를 확인하지는 않습니다.
    email = forms.EmailField()

    # auth앱의 PasswordResetForm에서는 save 메서드에서 이메일 발송에 필요한
    # 다양한 인자를 전달받습니다.
    def save(self, request: HttpRequest) -> None:
        email = self.cleaned_data.get("email")
        for uidb64, token in self.make_uidb64_and_token(email):
            scheme = "https" if request.is_secure() else "http"
            host = request.get_host()
            # 새로운 암호를 입력받아, 암호를 변경하는 뷰
            path = resolve_url(
                "accounts:password_reset_confirm", uidb64=uidb64, token=token
            )
            reset_url = f"{scheme}://{host}{path}"
            print(
                f"{email} 이메일로 {reset_url} 주소를 발송합니다."
            )  # TODO: 이메일 발송

    def make_uidb64_and_token(self, email: str) -> Iterator[tuple[str, str]]:
        for user in self.get_users(email):
            print(f"{email}에 매칭되는 유저를 찾았습니다.")

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            yield uidb64, token

    def get_users(self, email: str) -> Iterator[User]:
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        return (
            user
            for user in active_users
            if user.has_usable_password() and email == user.email
        )


class UsernameRecoveryForm(forms.Form):
    username = forms.CharField(label="사용자 아름", max_length=150)
    email = forms.EmailField(label="이메일")
