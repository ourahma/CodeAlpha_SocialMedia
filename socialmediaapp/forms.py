from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,SetPasswordForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video']
        
        
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'required': 'required',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'required': 'required',
            'placeholder': 'Last Name'
        })
    )
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'placeholder': 'User Name'
        })
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'required': 'required',
            'placeholder': 'Password'
        })
    )
    email = forms.EmailField(
        label="", 
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'required': 'required',
            'placeholder': 'Email'
        })
    )
    gender = forms.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio'
        })
    )
    terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox', 
            'checked': 'checked'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name','username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        # Customize help_texts and attributes for all fields
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

        # Custom placeholders for password fields
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''

        # Clean username method to avoid duplicate usernames
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username

