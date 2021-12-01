"""Forms for the microblogs app."""
from django import forms
from django.core.validators import RegexValidator
from .models import User, Club, Member

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class SignUpForm(forms.ModelForm):  
    """Form enabling unregistered users to sign up."""
    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'chess_experience', 'personal_statement']
        widgets = { 'bio': forms.Textarea(), 'personal_statement': forms.Textarea() }

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            bio=self.cleaned_data.get('bio'),
            chess_experience=self.cleaned_data.get('chess_experience'),
            personal_statement=self.cleaned_data.get('personal_statement'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'chess_experience', 'personal_statement']
        widgets = { 'bio': forms.Textarea(), 'personal_statement': forms.Textarea() }

class ApplicationForm(forms.Form):
    clubs = Club.objects.all()
    days = forms.ChoiceField(label="Choose a club:", choices=[(x.name, x.name) for x in clubs])
