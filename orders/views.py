
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from product.models import *
from myshop.forms import SearchForm
from orders.models import *
from django.contrib.auth.models import User
from user.models import *
from myshop.forms import ShopCartForm, WishListForm, OrderForm
import os
import stripe
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def index(request):
    return HttpResponse("Order Page")

# orders/views.py

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Add this to your .env

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.payment_intent = payment_intent['id']
            order.save()
        except Order.DoesNotExist:
            pass
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle payment failure (e.g., notify user)
    # ... handle other event types ...

    return HttpResponse(status=200)


@csrf_protect  # Since we're handling CSRF via AJAX, ensure security elsewhere
def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            order_code = data.get('order_id')

            # Retrieve the order
            order = Order.objects.get(code=order_code, user=request.user)

            # Create a Payment Intent with the order amount
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Amount in cents
                currency='usd',  # Change to your currency
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                metadata={'order_id': order.id},
            )

            if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
                # Tell the client to handle the action
                return JsonResponse({
                    'requires_action': True,
                    'payment_intent_client_secret': intent.client_secret
                })
            elif intent.status == 'succeeded':
                # The payment didn’t need any additional actions and completed!
                # Update the order as paid
                order.paid = True
                order.payment_intent = intent.id
                order.save()
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/received/'  # Adjust to your success URL
                })
            else:
                # Invalid status
                return JsonResponse({'error': 'Invalid PaymentIntent status'}, status=400)

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            return JsonResponse({'error': e.user_message}, status=400)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url='/login/')  # Check login
def addtoshopcart(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session information
    checkproduct = ShopCart.objects.filter(product_id=id, user_id=current_user.id)
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        messages.error(request, "Product does not exist.")
        return HttpResponseRedirect(url)

    if checkproduct.exists():
        control = 1  # The product is in the cart
    else:
        control = 0

    if request.method == 'POST':  # if there is a post
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:  # Update shopcart
                data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()  # save data
            else:  # Insert to Shopcart
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.quantity = form.cleaned_data['quantity']
                data.save()
            messages.success(request, "Product added to Shopcart")
            return HttpResponseRedirect(url)
    else:
        if control == 1:
            data = ShopCart.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
        else:
            data = ShopCart()
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.save()
        messages.success(request, "Product added to Shopcart")
        return HttpResponseRedirect(url)


def shopcart(request):
    category = Category.objects.all()
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.product is not None:
            total += rs.product.price * rs.quantity

    total_product = 0
    for rs in shopcart:
        if rs.product is not None:
            total_product += rs.quantity

    context = {
        'shopcart': shopcart,
        'category': category,
        'total': total,
        'total_product': total_product,
    }
    return render(request, 'shopcart.html', context)


@login_required(login_url='/login/')  # Check login
def addtowishlist(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session information
    checkproduct = WishList.objects.filter(product_id=id, user_id=current_user.id)
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        messages.error(request, "Product does not exist.")
        return HttpResponseRedirect(url)

    if checkproduct.exists():
        control = 1  # The product is in the wishlist
    else:
        control = 0

    if request.method == 'POST':  # if there is a post
        form = WishListForm(request.POST)
        if form.is_valid():
            if control == 1:  # Update wishlist
                data = WishList.objects.get(product_id=id, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()  # save data
            else:  # Insert to Wishlist
                data = WishList()
                data.user_id = current_user.id
                data.product_id = id
                data.quantity = form.cleaned_data['quantity']
                data.save()
            messages.success(request, "Product added to WishList")
            return HttpResponseRedirect(url)
    else:
        if control == 1:
            data = WishList.objects.get(product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
        else:
            data = WishList()
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.save()
        messages.success(request, "Product added to WishList")
        return HttpResponseRedirect(url)


def wishlist(request):
    category = Category.objects.all()
    current_user = request.user
    wishlist = WishList.objects.filter(user_id=current_user.id)
    total = 0
    for rs in wishlist:
        if rs.product is not None:
            total += rs.product.price * rs.quantity

    total_product = 0
    for rs in wishlist:
        if rs.product is not None:
            total_product += rs.quantity

    context = {
        'wishlist': wishlist,
        'category': category,
        'total': total,
        'total_product': total_product,
    }
    return render(request, 'wishlist.html', context)


@login_required(login_url='/login/')  # Ensure correct login URL
def checkout(request):
    category = Category.objects.all()
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)

    # Calculate total and total_product using generator expressions
    total = sum(rs.product.price * rs.quantity for rs in shopcart if rs.product is not None)
    total_product = sum(rs.quantity for rs in shopcart if rs.product is not None)

    # Attempt to get or create UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=current_user,
        defaults={'image': 'images/users/user.png'}
    )
    if created:
        messages.info(request, 'User profile created automatically.')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create Order instance without committing to add additional fields
            data = form.save(commit=False)
            data.user = current_user
            data.total = total
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(10).upper()
            data.code = ordercode
            data.save()

            # Create OrderProduct instances and update Product quantities
            for rs in shopcart:
                if rs.product is not None:
                    detail = OrderProduct()
                    detail.order = data
                    detail.product = rs.product
                    detail.user = current_user
                    detail.quantity = rs.quantity
                    detail.price = rs.product.price
                    detail.amount = rs.product.price * rs.quantity  # Correct calculation
                    detail.save()

                    # Update product quantity
                    rs.product.quantity -= rs.quantity
                    rs.product.save()

            # Clear ShopCart and reset session cart_items
            ShopCart.objects.filter(user_id=current_user.id).delete()
            request.session['cart_items'] = 0
            messages.success(request, "Your Order has been placed successfully!")

            # Create a Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),  # Amount in cents
                currency='usd',  # Change to your currency
                metadata={'order_id': data.id},
            )

            context = {
                'ordercode': ordercode,
                'category': category,
                'client_secret': intent.client_secret,
                'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY'),
            }

            return render(request, 'received.html', context)
        else:
            messages.warning(request, form.errors)
            return redirect("/checkout/")
    else:
        form = OrderForm()

    context = {
        'shopcart': shopcart,
        'category': category,
        'total': total,
        'total_product': total_product,
        'form': form,
        'profile': profile,
        'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY'),
    }

    return render(request, 'checkout.html', context)

@login_required(login_url='/login/')  # Check login
def deletefromcart(request, id):
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Your item has been deleted from Shopcart.")
    return HttpResponseRedirect("/shopcart")


@login_required(login_url='/login/')  # Check login
def deletefromwishlist(request, id):
    url = request.META.get('HTTP_REFERER')
    WishList.objects.filter(id=id).delete()
    messages.success(request, "Your item has been deleted from Wishlist.")
    return HttpResponseRedirect(url)  

