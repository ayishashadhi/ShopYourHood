from django import forms
from .models import CustomUser, CustomerProfile, ShopProfile
from django.contrib.auth.forms import UserCreationForm

# Customer Registration Form
class CustomerRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'phone', 'address', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.email = self.cleaned_data['email']
        user.user_type = 1  # Set user type to customer
        if commit:
            user.save()
            # Create the customer profile after saving the user
            CustomerProfile.objects.create(user=user, name=user.name, phone=user.phone, address=user.address)
        return user

# Shop Owner Registration Form
class ShopOwnerRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)
    email = forms.EmailField()
    owner_name = forms.CharField(max_length=255)
    shop_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=255)
    shop_proof = forms.ImageField()

    class Meta:
        model = CustomUser
        fields = [
            'username', 'name', 'phone', 'address', 'email', 'password1', 'password2', 'owner_name', 'shop_number','location', 'shop_proof'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.email = self.cleaned_data['email']
        user.user_type = 2  # Set user type to shop owner
        if commit:
            user.save()
            # Create the shop profile after saving the user
            ShopProfile.objects.create(user=user,
                                       name=self.cleaned_data['name'],
                                       phone=self.cleaned_data['phone'],
                                       address=self.cleaned_data['address'],
                                       owner_name=self.cleaned_data['owner_name'],
                                       shop_number=self.cleaned_data['shop_number'],
                                       location=self.cleaned_data['location'],
                                       shop_proof=self.cleaned_data['shop_proof'])
        return user
