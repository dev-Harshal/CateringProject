from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from UserApp.models import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    return render(request,'index.html')

def category(request):
    data = Category.objects.all()
    return render(request,'category.html',context={'data':data})


def option(request,id):
    data = Option.objects.filter(category = id).all()
    return render(request,'option.html',context={'data':data})


def dish(request,id):
    data = Dish.objects.filter(option = id).all()
    if request.user.is_authenticated:
        data1 = []
        
        for dish in data:
            dish_dict = {
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'image': dish.image,
                'cart_item_exists': CartItem.objects.filter(user=request.user, dish=dish.id,in_cart=True).exists(),
                # Add other attributes as needed
            }
            data1.append(dish_dict)
        data = data1    
    return render(request,'dish.html',context={'data':data})

def add_to_cart(request, id):
    # Get the Dish object
    dish = get_object_or_404(Dish, id=id)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the dish is already in the user's cart
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            dish=dish,
            in_cart = True
        )
        op = cart_item.dish.option.id
        # If the item already exists in the cart, delete it
        if not created:
            cart_item.delete()
            
        return redirect(f"/dish/{op}")  # Replace 'your_cart_url_name' with the actual URL name for your cart page
    else:
        return redirect('login-page')  # Replace 'your_login_url_name' with the actual URL name for your login page
    
@login_required(login_url='/login/')
def cart(request):
    count = 1
    if request.method == 'POST':
        count = request.POST.get('count')

    data = CartItem.objects.filter(user = request.user,in_cart=True)
    total = 0
    for obj in data:
        total = total + int(obj.dish.price)
    print(total)
    total = total * int(count)
    return render(request,'cart.html',context={'items':data,'total':total})


def loginPageView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None and user.role == 'User':
            login(request, user)
            return redirect('category')
        else:
            return render(request, "Auth/login.html")
    return render(request, "Auth/login.html")


def logoutPageView(request):
    logout(request)
    return redirect('index')

def signupPageView(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        if Users.objects.filter(email=email).exists():
            return render(request, "Auth/signup.html")
        if password == re_password:
            user = Users(full_name=str(full_name).title(), email=str(email).lower(), password=password,username=str(email).lower())
            user.save()
            return redirect('login-page')
        else:
            return render(request, "Auth/signup.html")
    return render(request, "Auth/signup.html")

def book_order(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        venue = request.POST.get('venue')
        count = request.POST.get('count')
        cart_items = CartItem.objects.filter(user=request.user,in_cart=True)        
        total = 0
        for cart_item in cart_items:
            total += int(cart_item.dish.price)

         
        total *= int(count)
        if total == 0:
            pass
            return redirect('cart')
        else:
        # Create the Order object
            order_obj = Order.objects.create(user=request.user, venue=venue, guest_count=count,total_price = total,name=name,phone=phone,date=date,time=time) # Save the Order object to get an ID assigned

            # Get the CartItems for the user


            # Use set() to assign the related items to the many-to-many field
            order_obj.items.set(cart_items)

            order_obj.update_inventory()
            order_obj.clear_cart()
            order_obj.save()
            return redirect('order')

    return render(request, 'book_order.html')


@login_required(login_url='/login/')
def order(request):
    data = Order.objects.filter(user = request.user)
    return render(request, 'order.html',context={'data':data})