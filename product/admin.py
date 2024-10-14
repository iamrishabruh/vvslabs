import admin_thumbnails
from django.contrib import admin, messages
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product
from product import models
from product.models import *
from django.urls import path
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from .models import Product
from myshop.forms import CSVUploadForm
import csv
from io import TextIOWrapper
import decimal


class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('title',)}
    # prepopulated_fields = {'slug': ('title',)}
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'

@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1


@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_thumbnail']
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'sku', 'stock', 'price', 'image_tag']
    list_filter = ['category', 'status']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='product_upload_csv'),
        ]
        return custom_urls + urls
    
    def generate_unique_slug(self, category_name):
        base_slug = slugify(category_name)
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                try:
                    decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                    reader = csv.DictReader(decoded_file)

                    products_created = 0
                    products_skipped = 0
                    error_messages = []

                    for row_number, row in enumerate(reader, start=2):  # Start at 2 considering header
                        try:
                            # Extract and clean data from each row
                            title = row.get('title')
                            category_name = row.get('category')
                            status = row.get('status')
                            slug = row.get('slug', '').strip()
                            sku = row.get('sku', '').strip()
                            stock = row.get('stock', '0').strip()
                            price = row.get('price', '0').strip()

                            # Diamond Specific Fields
                            metal_type = row.get('metal_type', '10kt White Gold').strip()
                            style = row.get('style', 'Crosses').strip()
                            carats_total_weight = row.get('carats_total_weight', '1/2 Ct.t.w.').strip()
                            primary_gem_type = row.get('primary_gem_type', 'Diamond').strip()
                            primary_gem_shape = row.get('primary_gem_shape', 'Round').strip()
                            primary_gem_color_clarity = row.get('primary_gem_color_clarity', 'G-H / I3').strip()
                            length_mm = row.get('length_mm', '0').strip()
                            width_mm = row.get('width_mm', '0').strip()
                            gram_weight = row.get('gram_weight', '0').strip()

                            # Validate required fields
                            if not title or not category_name:
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Missing required fields.")
                                continue

                            # Validate and parse numeric fields
                            try:
                                stock = int(stock)
                                price = decimal.Decimal(price)
                                length_mm = decimal.Decimal(length_mm)
                                width_mm = decimal.Decimal(width_mm)
                                gram_weight = decimal.Decimal(gram_weight)
                            except (ValueError, decimal.InvalidOperation):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid numeric value.")
                                continue

                            # Check for duplicates based on SKU or title
                            if sku:
                                if Product.objects.filter(sku=sku).exists():
                                    products_skipped += 1
                                    error_messages.append(f"Row {row_number}: Product with SKU '{sku}' already exists. Skipping.")
                                    continue
                            if Product.objects.filter(title=title).exists():
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Product '{title}' already exists. Skipping.")
                                continue

                            # Get or create the category
                            category, created = Category.objects.get_or_create(title=category_name)

                            # Validate choice fields
                            if metal_type not in dict(Product.METAL_TYPE_CHOICES):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid metal_type '{metal_type}'.")
                                continue
                            if style not in dict(Product.STYLE_CHOICES):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid style '{style}'.")
                                continue
                            if carats_total_weight not in dict(Product.CARATS_TOTAL_WEIGHT_CHOICES):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid carats_total_weight '{carats_total_weight}'.")
                                continue
                            if primary_gem_type not in dict(Product.PRIMARY_GEM_TYPE_CHOICES):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid primary_gem_type '{primary_gem_type}'.")
                                continue
                            if primary_gem_shape not in dict(Product.PRIMARY_GEM_SHAPE_CHOICES):
                                products_skipped += 1
                                error_messages.append(f"Row {row_number}: Invalid primary_gem_shape '{primary_gem_shape}'.")
                                continue

                            # Create the product
                            product = Product.objects.create(
                                title=title,
                                category=category,
                                status=status,
                                slug=slug or None,
                                sku=sku or None,
                                stock=stock,
                                price=price,
                                metal_type=metal_type,
                                style=style,
                                carats_total_weight=carats_total_weight,
                                primary_gem_type=primary_gem_type,
                                primary_gem_shape=primary_gem_shape,
                                primary_gem_color_clarity=primary_gem_color_clarity,
                                length_mm=length_mm,
                                width_mm=width_mm,
                                gram_weight=gram_weight,
                                # Add other fields as necessary
                            )
                            products_created += 1

                        except Exception as e:
                            products_skipped += 1
                            error_messages.append(f"Row {row_number}: Unexpected error: {e}")

                    # Provide feedback to the user
                    if products_created:
                        self.message_user(request, f"Successfully uploaded {products_created} products.", messages.SUCCESS)
                    if products_skipped:
                        self.message_user(request, f"Skipped {products_skipped} products. Check errors for details.", messages.WARNING)
                    for error in error_messages:
                        self.message_user(request, error, messages.ERROR)

                    return redirect('..')  # Redirect to the product list page

                except Exception as e:
                    self.message_user(request, f"An error occurred while processing the file: {e}", messages.ERROR)

        else:
            form = CSVUploadForm()

        context = {
            'form': form,
            'title': 'Upload CSV',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return TemplateResponse(request, "upload_csv_form.html", context)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','subject','comment', 'status','create_at']
    list_filter = ['status']
    readonly_fields = ('subject','comment','ip','user','product','rate','id')


admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Comment,CommentAdmin)
