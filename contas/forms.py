from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import ROLE_CHOICES, Profile

User = get_user_model()


def split_name(full_name):
    """Separa o nome completo em primeiro nome e sobrenome."""
    first, _, last = full_name.strip().partition(' ')
    return first, last.strip()


def email_in_use(email, exclude_pk=None):
    users = User.objects.filter(email__iexact=email)
    if exclude_pk is not None:
        users = users.exclude(pk=exclude_pk)
    return users.exists()


class SignupForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nome', max_length=300,
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'autofocus': True}),
    )
    email = forms.EmailField(
        label='E-mail',
        help_text='Usado para recuperar a senha.',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['full_name', 'email', 'username']
        labels = {'username': 'Nome de usuário'}
        help_texts = {'username': 'Até 150 caracteres: letras, números e @ . + - _'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if email_in_use(email):
            raise forms.ValidationError('Já existe uma conta com esse e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name, user.last_name = split_name(self.cleaned_data['full_name'])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.for_user(user)
        return user


class ProfileForm(forms.ModelForm):
    """Edita, numa tela só, os dados do usuário e os do perfil."""

    full_name = forms.CharField(label='Nome', max_length=300)
    email = forms.EmailField(
        label='E-mail',
        help_text='Não aparece no perfil público. É para onde vai o link de recuperação de senha.',
    )

    class Meta:
        model = Profile
        fields = ['age', 'fun_facts']
        labels = {'age': 'Idade', 'fun_facts': 'Curiosidades sobre você'}
        widgets = {
            'age': forms.NumberInput(attrs={'min': 0, 'max': 120}),
            'fun_facts': forms.Textarea(attrs={
                'rows': 6,
                'class': 'plain',
                'placeholder': 'Hobbies, o que você estuda, uma mania, a comida favorita do bandejão...',
            }),
        }

    field_order = ['full_name', 'email', 'age', 'fun_facts']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['full_name'].initial = user.get_full_name()
        self.fields['email'].initial = user.email

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if email_in_use(email, exclude_pk=self.instance.user_id):
            raise forms.ValidationError('Já existe outra conta com esse e-mail.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name, user.last_name = split_name(self.cleaned_data['full_name'])
        user.email = self.cleaned_data['email']
        if commit:
            user.save(update_fields=['first_name', 'last_name', 'email'])
            profile.save()
        return profile


class AccessForm(forms.Form):
    role = forms.ChoiceField(label='Nível', choices=ROLE_CHOICES)
    is_active = forms.BooleanField(label='Conta ativa', required=False)
