from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from math import floor
from .models import  Tshirt,SizeVariant,Cart,Order,OrderItem,Payment,Occasion,Sleeve,NeckType,Brand,Color,IdealFor
from django.contrib.auth import authenticate ,login as loginUser,logout as logoutUser
from store.forms.authforms import CustomerCreationForm ,CustomerAuthenticationForm
from store.forms.checkout_form import CheckoutOrderForm
from Tshirts_shop.settings import API_KEY, AUTH_TOKEN
from instamojo_wrapper import Instamojo
from django.core.paginator import Paginator
from urllib.parse import urlencode

api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/');

# Create your views here.

class Index(View):
    def get(self, request):


        brand=request.GET.get('brand')
        color = request.GET.get('color')
        occasion = request.GET.get('occasion')
        idealfor = request.GET.get('idealfor')
        sleeve = request.GET.get('sleeve')
        necktype = request.GET.get('necktype')
        page = request.GET.get('page')

        if page is None or page =='':
            page=1

        products = Tshirt.objects.all()

        if brand:
            products = products.filter(brand__slug=brand)

        if color:
            products = products.filter(color__slug=color)

        if occasion:
            products = products.filter(occasion__slug=occasion)

        if necktype:
            products = products.filter(neck_type__slug=necktype)

        if sleeve:
            products = products.filter(sleeve__slug=sleeve)

        if idealfor:
            products = products.filter(ideal_f*or__slug=idealfor)



        brands = Brand.objects.all()
        colors = Color.objects.all()
        occasions = Occasion.objects.all()
        idealfors = IdealFor.objects.all()
        sleeves = Sleeve.objects.all()
        necktypes = NeckType.objects.all()

        cart=request.session.get('cart')

        paginator=Paginator(products,4)
        page_obj=paginator.get_page(page)

        query=request.GET.copy()
        query['page']=''
        pageurl=urlencode(query)

        context = {'page_obj': page_obj,
                 'brands': brands,
                 'colors': colors,
                 'occasions': occasions,
                 'idealfors': idealfors,
                 'sleeves': sleeves,
                 'necktypes': necktypes,
                 'pageurl':pageurl,
                 }

        return render(request, 'store/index.html', context=context)


def cart(request):
    cart=request.session.get('cart')
    if cart is None:
        cart=[]

    for cart_obj in cart:
        tshirt_id=cart_obj.get('tshirt')
        size_temp = cart_obj.get('size')
        tshirt_obj=Tshirt.objects.get(id=tshirt_id)
        cart_obj['tshirt']=tshirt_obj
        cart_obj['size']= SizeVariant.objects.get(tshirt=tshirt_id, size=size_temp)
    return render(request,'store/cart.html',{'cart':cart})

class Login(View):
    def get(self, request):
        form = CustomerAuthenticationForm()
        next_page=request.GET.get('next')

        if next_page is not None:
            request.session['next_page']=next_page


        return render(request, 'store/login.html',context={'form': form})

    def post(self, request):
        form = CustomerAuthenticationForm(data=request.POST)
        if form.is_valid():
            email=form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user=authenticate(username=email,password=password)
            if user:
                loginUser(request,user)

                # add cart in session
                session_cart=  request.session.get('cart')
                if session_cart is None:
                    session_cart=[]
                else:
                    for cart_obj in session_cart:
                        size = cart_obj.get('size')
                        quantity = cart_obj.get('quantity')
                        tshirt = cart_obj.get('tshirt')
                        sizevariant = SizeVariant.objects.get(size=size, tshirt=tshirt)

                        database_cart_obj=Cart()
                        database_cart_obj.user = user
                        database_cart_obj.sizeVariant = sizevariant
                        database_cart_obj.quantity = quantity
                        database_cart_obj.save()

                # add cart in database
                cart_objects=Cart.objects.filter(user=user)
                session_cart_list=[]
                for cart_obj in cart_objects:
                    session_cart_obj={
                        'size' : cart_obj.sizeVariant.size,
                        'tshirt' : cart_obj.sizeVariant.tshirt.id,
                        'quantity': cart_obj.quantity
                    }
                    session_cart_list.append(session_cart_obj)

                request.session['cart'] = session_cart_list

                next_page=request.session.get('next_page')
                if next_page is None:
                    next_page='index'

                return redirect(next_page)

        return render(request, 'store/login.html', context={'form': form})
       


def logout(request):
    logoutUser(request)
    return redirect('index')


class Signup(View):
    def get(self, request):
        form = CustomerCreationForm()
        context_form={'form':form}
        return render(request, 'store/signup.html',context=context_form)


    def post(self, request):
        print(request.POST)
        
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email=user.username
            user.save()
            print(user)
            return redirect('login')

        context_form = {'form': form}
        return render(request, 'store/signup.html', context=context_form)


def show_product_details(request ,slug):
    tshirt = Tshirt.objects.get(slug=slug)
    size = request.GET.get('size')
    if size is None:
        size=tshirt.sizevariant_set.all().order_by('prize').first()
    else:
        size = tshirt.sizevariant_set.get(size=size)

    discount = floor(size.prize - (size.prize * (tshirt.descount)/100))
    context = {'tshirt' : tshirt , 'price': size.prize , 'discount' : discount , 'active_size': size}

    return render(request, 'store/show_product_details.html',context=context)


def add_to_cart(request,slug,size):
    user = None
    if request.user.is_authenticated:
        user=request.user

    cart= request.session.get('cart')
    if cart is None:
        cart=[]

    tshirt=Tshirt.objects.get(slug=slug)

    add_cart_for_anom_user(cart,size,tshirt)

    if user is not None:
        add_cart_to_database(user,size,tshirt)


    request.session['cart']=cart
    return_url=request.GET.get('return_url')
    return redirect(return_url)


def add_cart_to_database(user,size,tshirt):
    sizevariant_obj = SizeVariant.objects.get(size=size, tshirt=tshirt)
    existing_cart_object = Cart.objects.filter(user=user, sizeVariant=sizevariant_obj)
    if len(existing_cart_object) > 0:
        obj = existing_cart_object[0]
        obj.quantity = obj.quantity + 1
        obj.save()

    else:
        cart_object = Cart()
        cart_object.user = user
        cart_object.sizeVariant = sizevariant_obj
        cart_object.quantity = 1
        cart_object.save()


def add_cart_for_anom_user(cart,size,tshirt):
    flag=False
    for cart_obj in cart:
        tshirt_id=cart_obj.get('tshirt')
        size_type = cart_obj.get('size')
        if tshirt_id == tshirt.id and size==size_type:
            flag=True
            quantity=cart_obj['quantity']
            cart_obj['quantity']=quantity+1

    if not flag :
        cart_obj={
            'tshirt':tshirt.id,
            'size':size,
            'quantity': 1
        }
        cart.append(cart_obj)

#utility function
def total_payable_amount(cart):
    total=0
    for cart_obj in cart:
        tshirt_obj=cart_obj.get('tshirt')
        sizevariant=cart_obj.get('size')
        quantity = cart_obj.get('quantity')

        discount = tshirt_obj.descount
        price = sizevariant.prize

        sale_prices = floor(price - (price * (discount / 100)))
        total_of_single_product= sale_prices*quantity
        total = total + total_of_single_product
    return total



@login_required(login_url='/login')
def checkout(request):
    if request.method == 'GET':
        form = CheckoutOrderForm()
        cart_list = request.session.get('cart')
        if cart_list is None:
            cart_list = []
        else:
            for cart_obj in cart_list:
                size = cart_obj.get('size')
                tshirt_id = cart_obj.get('tshirt')
                sizevariant = SizeVariant.objects.get(size=size, tshirt=tshirt_id)
                cart_obj['tshirt'] = sizevariant.tshirt
                cart_obj['size'] = sizevariant


        return render(request, 'store/checkout.html', {'form': form, 'cart_list': cart_list})

    else:
        #post request
        form=CheckoutOrderForm(request.POST)
        user=None
        if request.user.is_authenticated:
            user=request.user

        if form.is_valid():
            cart_list = request.session.get('cart')
            if cart_list is None:
                cart_list = []

            for cart_obj in cart_list:
                size = cart_obj.get('size')
                tshirt_id = cart_obj.get('tshirt')
                quqntity = cart_obj.get('quantity')
                sizevariant = SizeVariant.objects.get(size=size, tshirt=tshirt_id)
                cart_obj['tshirt'] = sizevariant.tshirt
                cart_obj['size'] = sizevariant



            shipping_address=form.cleaned_data.get('shipping_address')
            phone=form.cleaned_data.get('phone')
            payment_method= form.cleaned_data.get('payment_method')
            total=total_payable_amount(cart_list)
            print(shipping_address,phone,payment_method,total)

            #order inserting in database
            order=Order()
            order.shipping_address=shipping_address
            order.phone=phone
            order.payment_method=payment_method
            order.total=total
            order.order_status='PENDING'
            order.user=user
            order.save()

            #save order items in databases
            print(cart_list)
            for cart_obj in cart_list:
                sizevariant = cart_obj.get('size')
                tshirt_obj= cart_obj.get('tshirt')
                quantity = cart_obj.get('quantity')

                order_item=OrderItem()
                order_item.order=order
                order_item.tshirt=tshirt_obj
                order_item.sizeVariant=sizevariant
                order_item.quantity=quantity
                order_item.price=floor(sizevariant.prize - (sizevariant.prize* (tshirt_obj.descount / 100)))
                order_item.save()

            # Create a new Payment Request
            response = api.payment_request_create(
                amount=order.total,
                purpose='pay for product',
                send_email=True,
                email=user.email,
                buyer_name=f'{user.first_name} {user.last_name}',
                redirect_url="http://localhost:8000/validate_payment"
                )


            url=response['payment_request']['longurl']
            payment_request_id=response['payment_request']['id']

            payment=Payment()
            payment.order=order
            payment.payment_request_id=payment_request_id
            payment.save()
            return redirect(url)

        else:
            return redirect('checkout')


def validate_payment(request):
    user=None
    if request.user.is_authenticated:
        user=request.user

    payment_request_id=request.GET.get('payment_request_id')
    payment_id = request.GET.get('payment_id')

    print(payment_request_id,payment_id)
    response = api.payment_request_payment_status(payment_request_id, payment_id)
    status=response.get('payment_request').get('payment').get('status')

    if status != "Failed":
        print('success')
        try:
            payment=Payment.objects.get(payment_request_id=payment_request_id)
            payment.payment_id=payment_id
            payment.payment_status=status
            payment.save()

            order=payment.order
            order.order_status="PLACED"
            order.save()
            cart=[]
            request.session['cart']=cart

            Cart.objects.filter(user=user).delete()

            return redirect('order')
        except:
            return render(request,'store/payment_failed.html')
    else:
        return render(request, 'store/payment_failed.html')




@login_required(login_url='/login')
def order(request):

    user=request.user
    orders=Order.objects.filter(user=user).order_by('-date').exclude(order_status='PENDING')
    context={'orders': orders }


    return render(request,'store/order.html',context=context)

