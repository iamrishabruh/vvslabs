import admin_thumbnails
from django.contrib import admin
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
    list_display = ['title', 'category', 'status', 'image_tag']
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}

    # Step 2.2: Add Custom Admin URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='product_upload_csv'),
        ]
        return custom_urls + urls

    # Step 2.3: Define the CSV Upload View
    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                try:
                    # Decode the uploaded file
                    decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
                    reader = csv.DictReader(decoded_file)
                    
                    # Initialize counters for feedback
                    products_created = 0
                    products_skipped = 0
                    error_messages = []

                    for row in reader:
                        # Extract and clean data from each row
                        title = row.get('title')
                        category = row.get('category')
                        status = row.get('status')
                        slug = row.get('slug', '')  # If slug is provided
                        # Add other fields as necessary

                        # Basic validation
                        if not title or not category:
                            products_skipped += 1
                            error_messages.append(f"Missing required fields in row: {row}")
                            continue

                        # Optionally, check for duplicates
                        if Product.objects.filter(title=title).exists():
                            products_skipped += 1
                            error_messages.append(f"Product with title '{title}' already exists. Skipping.")
                            continue

                        # Create the product
                        Product.objects.create(
                            title=title,
                            category=category,
                            status=status,
                            slug=slug or None,
                            # Add other fields as necessary
                        )
                        products_created += 1

                    # Provide feedback to the user
                    if products_created:
                        self.message_user(request, f"Successfully uploaded {products_created} products.", messages.SUCCESS)
                    if products_skipped:
                        self.message_user(request, f"Skipped {products_skipped} products. Check errors for details.", messages.WARNING)
                    for error in error_messages:
                        self.message_user(request, error, messages.ERROR)

                    return redirect('..')  # Redirect back to the product list

                except Exception as e:
                    self.message_user(request, f"An error occurred: {e}", messages.ERROR)
        else:
            form = CSVUploadForm()

        # Define the context for the template
        context = {
            'form': form,
            'title': 'Upload CSV',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return TemplateResponse(request, "admin/upload_csv_form.html", context)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','subject','comment', 'status','create_at']
    list_filter = ['status']
    readonly_fields = ('subject','comment','ip','user','product','rate','id')


admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Comment,CommentAdmin)
