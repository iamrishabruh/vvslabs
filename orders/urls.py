from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addtoshopcart/<int:id>", views.addtoshopcart, name="addtoshopcart"),
    path('deletefromcart/<int:id>', views.deletefromcart, name='deletefromcart'),
    path("addtowishlist/<int:id>", views.addtowishlist, name="addtowishlist"),
    path('deletefromwishlist/<int:id>', views.deletefromwishlist, name='deletefromwishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),

]

