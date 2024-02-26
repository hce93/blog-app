from django import forms
from .models import Comments, Subscribe, Post
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields=['title', 'content', 'image', 'tags']
        widgets={
            'tags':forms.CheckboxSelectMultiple
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = "Title..."
        self.fields['content'].widget.attrs['placeholder'] = "Content..."
        self.fields['image'].widget.attrs['placeholder'] = "Name"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = {'content', 'name', 'email', 'website'}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = "Type your comment..."
        self.fields['email'].widget.attrs['placeholder'] = "Email"
        self.fields['name'].widget.attrs['placeholder'] = "Name"
        self.fields['website'].widget.attrs['placeholder'] = "Website"
        
class SubscribeForm(forms.ModelForm):
    class Meta:
        model =  Subscribe
        fields = '__all__'
        # remove labels from the form
        labels = {'email':_('')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = "Enter your email"
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Subscribe.objects.filter(email=email).exists():
            raise forms.ValidationError("email already subscribed!")
        return email
        
class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = {'username','email','password1','password2'}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "Username"
        self.fields['email'].widget.attrs['placeholder'] = "Email"
        self.fields['password1'].widget.attrs['placeholder'] = "Password"
        self.fields['password2'].widget.attrs['placeholder'] = "Repeat Password"
        
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        # check if user exists in the database
        new = User.objects.filter(username=username)
        if new.count():
            raise forms.ValidationError("User already exists")
        else:
            return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        new = User.objects.filter(email=email)
        if new.count():
            raise forms.ValidationError("Email already exists")
        else:
            return email
        
    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1!=password2:
            raise forms.ValidationError("Passwords don't match!")
        else:
            return password2