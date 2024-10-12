# orders/forms.py

from orders.models import ShopCart, WishList, Order
from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    catid = forms.IntegerField()

class ShopCartForm(forms.ModelForm):
    class Meta:
        model = ShopCart
        fields = ['quantity']

class WishListForm(forms.ModelForm):
    class Meta:
        model = WishList
        fields = ['quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'country', 'city', 'address_one', 'address_two',
            'postal_code'
        ]
