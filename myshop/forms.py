# orders/forms.py

from orders.models import ShopCart, WishList, Order
from django import forms
import csv


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

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='Maximum file size: 10MB',
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File is not CSV type')
        if csv_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File size exceeds 10MB')
        return csv_file