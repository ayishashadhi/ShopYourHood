from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .forms import CustomerRegistrationForm, ShopOwnerRegistrationForm
from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import never_cache

# Customer registration view
def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to customer login page
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register/customer_register.html', {'form': form})

# Shop owner registration view
def shop_owner_register(request):
    if request.method == 'POST':
        form = ShopOwnerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')   # Redirect to verification page
    else:
        form = ShopOwnerRegistrationForm()
    return render(request, 'register/shop_owner_register.html', {'form': form})


# customer dashboard 
@login_required
def customer_dashboard(request):
    customer_profile = request.user.customerprofile  # Access the related CustomerProfile
    return render(request, 'dashboard/customer_dashboard.html', {'customer_profile': customer_profile})

# Shop Dashboard 
@login_required
def shop_owner_dashboard(request):
    shop_profile = request.user.shopprofile
    
    if not shop_profile.is_verified:
        return redirect('shop_pending_verification')  # Redirect to a pending verification page
    
    return render(request, 'dashboard/shop_owner_dashboard.html')


# shop pending verification
@login_required
def shop_pending_verification(request):
    return render(request, 'dashboard/shop_pending_verification.html')


# users login 

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if user.user_type == 1:  # Customer
            return reverse('customer_dashboard')
        elif user.user_type == 2:  # Shop Owner
            return reverse('shop_owner_dashboard')
        elif user.user_type == 3: # admin
            return reverse('admin_dashboard')