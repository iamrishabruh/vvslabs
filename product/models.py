from django.db import models
import mptt
from mptt.admin import DraggableMPTTAdmin
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.auth.models import User
from django.forms import ModelForm

from django.db.models import Avg, Count
# Create your models here.
class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    parent = TreeForeignKey('self',blank=True, null=True ,related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    keywords = models.CharField(max_length=255)
    short_description=models.TextField(max_length=255)
    long_description=RichTextUploadingField()
    image=models.ImageField(blank=True,upload_to='images/')
    status=models.CharField(max_length=10, choices=STATUS)
    slug = models.SlugField(null=False, unique=True)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
   

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})    

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):                           # __str__ method elaborated later in
        full_path = [self.title]                  # post.  use __unicode__ in place of
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    def image_tag(self):
        if self.image is not None:
            return mark_safe('<div class="single-slider overlay" style="background-image: {}">'.format(self.image))
        else:
            return "No image"    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
class Product(models.Model):

    from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField  # Ensure django-ckeditor is installed and configured

class Product(models.Model):
    # Status Choices
    STATUS = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )
    status = models.CharField(max_length=12, choices=STATUS)
    # Gender Choices (if still applicable)
    GENDER = (
        ('None', 'None'),
        ('Men', 'Men'),
        ('Women', 'Women'),
    )
    gender = models.CharField(max_length=100, choices=GENDER, default='None')
    # Variant Choices
    VARIANTS = (
        ('None', 'None'),
        ('Color', 'Color'),
        ('Color-Size', 'Color-Size'), 
    )
    variant = models.CharField(max_length=20, choices=VARIANTS, default='None')
   
    # Category Relationship
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    long_description = RichTextUploadingField(default='Write Your long Description here')
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    additional_images = models.ImageField(upload_to='images/additional/', blank=True, null=True)  # Optional: For multiple images
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
  
    slug = models.SlugField(null=False, unique=True)
   
    
    num_of_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)

    # Diamond Specific Fields

    METAL_TYPE_CHOICES = (
        ('White Gold', 'White Gold'),
        ('Yellow Gold', 'Yellow Gold'),
        ('Rose Gold', 'Rose Gold'),
        ('Platinum', 'Platinum'),
        # Add more as needed
    )
    metal_type = models.CharField(max_length=50, choices=METAL_TYPE_CHOICES, default='10kt White Gold')

    STYLE_CHOICES = (
        ('Crosses', 'Crosses'),
        ('Rings', 'Rings'),
        ('Earrings', 'Earrings'),
        ('Bracelets', 'Bracelets'),
        ('Necklaces', 'Necklaces'),
        ('Pendants', 'Pendants'),
        # Add more as needed
    )
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='Crosses')

    CARATS_TOTAL_WEIGHT_CHOICES = (
        ('0.5 Ct.t.w.', '0.5 Ct.t.w.'),
        ('1 Ct.t.w.', '1 Ct.t.w.'),
        ('1.25 Ct.t.w.', '1.25 Ct.t.w.'),
        ('1.5 Ct.t.w.', '1.5 Ct.t.w.'),
        ('1.75 Ct.t.w.', '1.75 Ct.t.w.'),
        ('2 Ct.t.w.', '2 Ct.t.w.'),
        ('2.25 Ct.t.w.', '2.25 Ct.t.w.'),
        ('2.5 Ct.t.w.', '2.5 Ct.t.w.'),
        ('2.75 Ct.t.w.', '2.75 Ct.t.w.'),
        ('3 Ct.t.w.', '3 Ct.t.w.'),
        ('3.25 Ct.t.w.', '3.25 Ct.t.w.'),
        ('3.5 Ct.t.w.', '3.5 Ct.t.w.'),
        ('3.75 Ct.t.w.', '3.75 Ct.t.w.'),
        ('4 Ct.t.w.', '4 Ct.t.w.'),
        ('4.25 Ct.t.w.', '4.25 Ct.t.w.'),
        ('4.5 Ct.t.w.', '4.5 Ct.t.w')
        # Add more as needed
    )
    carats_total_weight = models.CharField(max_length=20, choices=CARATS_TOTAL_WEIGHT_CHOICES, default='1/2 Ct.t.w.')

    PRIMARY_GEM_TYPE_CHOICES = (
        ('Diamond', 'Diamond'),
        ('Sapphire', 'Sapphire'),
        ('Ruby', 'Ruby'),
        ('Emerald', 'Emerald'),
        # Add more as needed
    )
    primary_gem_type = models.CharField(max_length=50, choices=PRIMARY_GEM_TYPE_CHOICES, default='Diamond')

    PRIMARY_GEM_SHAPE_CHOICES = (
        ('Round', 'Round'),
        ('Princess', 'Princess'),
        ('Emerald', 'Emerald'),
        ('Oval', 'Oval'),
        ('Marquise', 'Marquise'),
        ('Cushion', 'Cushion'),
        ('Pear', 'Pear'),
        ('Heart', 'Heart'),
        # Add more as needed
    )
    primary_gem_shape = models.CharField(max_length=50, choices=PRIMARY_GEM_SHAPE_CHOICES, default='Round')

    primary_gem_color_clarity = models.CharField(
        max_length=50,
        default='G-H / I3',
        verbose_name="Primary Gem Color / Clarity",
        help_text="Format: Color/Clarity (e.g., G-H / I3)"
    )

    length_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Length (mm)",
        help_text="Length of the jewelry piece in millimeters"
    )
    width_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Width (mm)",
        help_text="Width of the jewelry piece in millimeters"
    )

    gram_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="Gram Weight",
        help_text="Weight of the jewelry piece in grams (approximately)"
    )
    
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)  # SKU field
    stock = models.PositiveIntegerField(default=0)  # Stock field
   

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
## method to create a fake table field in read only mode
    def image_tag(self):
        if self.image and self.image.url:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        return "No Image"

    def avaregereview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(avarage=Avg('rate'))
        avg=0
        if reviews["avarage"] is not None:
            avg=float(reviews["avarage"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(product=self, status='True').aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt        

class Images(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True, upload_to='images/')


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250,blank=True)
    email = models.CharField(max_length=250,blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status=models.CharField(max_length=10,choices=STATUS, default='New')
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
   

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate','email','name']

