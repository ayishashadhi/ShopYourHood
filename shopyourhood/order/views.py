from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Booking, CartItem, OrderRequest
from products.models import Product, ShopProduct
from django.urls import reverse
from authentication.models import ShopProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def choose_shop(request, product_id, action):   
    # Fetch only the verified product
    product = get_object_or_404(Product, id=product_id, is_verified=True)
    # Get all shops offering this product (already verified)
    shop_products = ShopProduct.objects.filter(product=product)
    
    if request.method == 'POST':
        shop_id = request.POST.get('shop_id')
        quantity = request.POST.get('quantity', 1)  # Get quantity from form, default to 1

        if shop_id:
            if action == 'cart':
                # Add the selected product to the cart with specified quantity
                CartItem.objects.create(
                    customer=request.user, 
                    product=product, 
                    shop_id=shop_id,
                    quantity=int(quantity)  # Convert to integer
                )
                return redirect(reverse('view_cart'))  # Redirect to view the cart after adding

            elif action == 'book':
                # Create a booking for the selected product
                booking = Booking.objects.create(
                    customer=request.user, 
                    product=product, 
                    shop_id=shop_id,
                    status='pending'
                )
                booking.start_timer()  # Start the booking timer

                # Create the order request for the shop owner
                shop_owner = ShopProfile.objects.get(id=shop_id).user  # Assuming ShopProfile has a user field
                OrderRequest.objects.create(booking=booking, shop_owner=shop_owner)

                return redirect('view_bookings')  # Redirect to the bookings page after booking

    return render(request, 'order/choose_shop.html', {
        'product': product,
        'shop_products': shop_products,
        'action': action
    })


# cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(customer=request.user)  # Get cart items for the logged-in user
    total_price = 0

    for item in cart_items:
        # Fetch the ShopProduct for each item in the cart
        try:
            shop_product = ShopProduct.objects.get(product=item.product, shop=item.shop)
            item.price = shop_product.price  # Store the price of the product
            item.total_item_price = shop_product.price * item.quantity  # Calculate total price for this item
            total_price += item.total_item_price  # Add to the overall total price
        except ShopProduct.DoesNotExist:
            item.price = 0  # Default price if not found
            item.total_item_price = 0  # Default total item price if not found

    return render(request, 'order/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })





@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        # Get the cart item to be removed
        cart_item = get_object_or_404(CartItem, id=item_id, customer=request.user)
        cart_item.delete()  # Remove the item from the cart

    return redirect('view_cart')  # Redirect back to the cart view




@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    
    for item in cart_items:
        # Create individual bookings based on the item's quantity
        for _ in range(item.quantity):
            booking = Booking.objects.create(
                customer=request.user,
                product=item.product,
                shop=item.shop,
                status='pending'
            )
            
            # Start the 24-hour timer on each booking
            booking.start_timer()
            
            # Create an order request tied to the booking for shop approval
            OrderRequest.objects.create(booking=booking, shop_owner=item.shop.user)
    
    # Clear cart after checkout
    cart_items.delete()
    
    return redirect('view_bookings')

@login_required
def estimate(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total_price = 0
    item_calculations = []

    for item in cart_items:
        # Fetch the ShopProduct to get the correct price
        try:
            shop_product = ShopProduct.objects.get(product=item.product, shop=item.shop)
            item_price = shop_product.price * item.quantity
            total_price += item_price
            item_calculations.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': shop_product.price,
                'total_price': item_price
            })
        except ShopProduct.DoesNotExist:
            continue  # Skip if the shop product isn't found

    return render(request, 'order/estimate.html', {
        'item_calculations': item_calculations,
        'total_price': total_price,
    })





# Create booking

# @login_required
# def make_booking(request, product_id, shop_id):
#     product = get_object_or_404(Product, id=product_id)
#     shop = get_object_or_404(ShopProfile, id=shop_id)
#     booking = Booking(customer=request.user, product=product, shop=shop, status='pending')
#     booking.save()

#     booking.start_timer()

#     shop_owner = shop.user
#     OrderRequest.objects.create(booking=booking, shop_owner=shop_owner)
#     return redirect('view_bookings')


# customer view booking
@login_required
def view_bookings(request):
    bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'order/view_bookings.html', {'bookings': bookings})



# shop owner request list
@login_required
def shop_owner_requests(request):
    requests = OrderRequest.objects.filter(shop_owner=request.user)
    for req in requests:
        if req.booking.expires_at:  # Check if expires_at is not None
            req.remaining_time = req.booking.expires_at - timezone.now()
        else:
            req.remaining_time = None  # or set to zero/another default value if needed
    return render(request, 'order/shop_owner_requests.html', {'requests': requests})




#shop owner request verify
@login_required
def handle_order_request(request, request_id, action):
    order_request = get_object_or_404(OrderRequest, id=request_id, shop_owner=request.user)
    if action == 'approve':
        # Update the OrderRequest status to 'approved'
        order_request.status = 'approved'
        order_request.save()

        # Update the related Booking status to 'approved'
        booking = order_request.booking
        booking.status = 'approved'
        booking.save()
    elif action == 'reject':
        booking_id = order_request.booking.id  # Store booking ID for deletion
        order_request.reject()
        order_request.delete()  # Delete the order request from the OrderRequest table
        Booking.objects.filter(id=booking_id).delete()
    return redirect('shop_owner_requests')