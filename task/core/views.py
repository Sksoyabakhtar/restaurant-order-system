from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from .models import Item, Order
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import F
import uuid




def signup(request):
    if request.method == 'POST':
        # Get the form data from the POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')
        
        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Optionally log the user in immediately after registration
        login(request, user)

        # Redirect to the login page after successful signup
        messages.success(request, "Signup successful! Please login.")
        return redirect('login')

    return render(request, 'signup.html')



def login_user(request):
    if request.method == 'POST':
        # Get the data manually from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('order_page')  # Redirect to order page after login
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')



from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.timezone import localtime

@login_required
def order_page(request):
    items = Item.objects.all()  # Fetch all items
    return render(request, 'order_page.html', {'items': items})



from .models import Order, Item
import random
import string
from django.utils import timezone


def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@login_required
def place_order(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('item_ids')
        order_date_str = request.POST.get('order_date', timezone.localtime(timezone.now()).date())  # Get the selected date or default to today
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()  # Convert the string to datetime.date

        order_details = []
        for item_id in selected_items:
            item = Item.objects.get(id=item_id)
            quantity = int(request.POST.get(f'quantity_{item_id}', 0))
            instruction = request.POST.get(f'instruction_{item_id}', '')

            # Check if the user has already ordered the same item on the selected date
            if Order.objects.filter(user=request.user, item=item, order_date=order_date).exists():
                messages.error(request, f"You have already ordered {item.name} on {order_date}. You cannot order it again on the same day.")
                return redirect('order_page')

            # Create the order if not already placed on the selected date
            order_id = generate_order_id()  # Assuming this function generates an order ID
            total_price = item.price * quantity
            order = Order.objects.create(
                order_id=order_id,
                item=item,
                quantity=quantity,
                total_price=total_price,
                special_instruction=instruction,
                user=request.user,
                created_at=timezone.make_aware(datetime.combine(order_date, datetime.min.time())),  # Set the created_at to the selected date
                order_date=order_date  # Store the order date
            )
            item.stock -= quantity  # Reduce stock
            item.save()  # Save item changes
            order_details.append(order)

        # Redirect to the order list page with a success message
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_list')

    return redirect('order_page')



@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})








































