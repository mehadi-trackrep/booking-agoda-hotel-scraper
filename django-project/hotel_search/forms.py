from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    # Optionally add email field if you want login via email
    # email = forms.EmailField(required=False, help_text="Optional")

    class Meta:
        model = User
        fields = ["username", "password"]

class HotelSearchForm(forms.Form):
    city = forms.CharField(label='City', max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., London'}))
    price_range = forms.CharField(label='Max Price (in your currency)', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 150'}))
    star_rating = forms.ChoiceField(label='Minimum Star Rating', required=False,
        choices=[('', 'Any'), ('1', '1 Star'), ('2', '2 Stars'), ('3', '3 Stars'), ('4', '4 Stars'), ('5', '5 Stars')])