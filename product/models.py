from django.db import models
import mptt
from mptt.admin import DraggableMPTTAdmin
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
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
    def __str__(self):
        return self.title

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
            return ""    

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField  # Ensure django-ckeditor is installed and configured

class Product(models.Model):
    # Status Choices
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    # Gender Choices (if still applicable)
    GENDER = (
        ('None', 'None'),
        ('Men', 'Men'),
        ('Women', 'Women'),
    )

    # Variant Choices
    VARIANTS = (
        ('None', 'None'),
        ('Color', 'Color'),
        ('Color-Size', 'Color-Size'), 
    )

    # Category Relationship
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    # Basic Product Information
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    long_description = RichTextUploadingField(default='Write Your long Description here')

    # Image and Media
    image = models.ImageField(upload_to='images/', null=False)
    additional_images = models.ImageField(upload_to='images/additional/', blank=True, null=True)  # Optional: For multiple images

    # Pricing and Inventory
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)

    # Gender (if still applicable)
    gender = models.CharField(max_length=100, choices=GENDER, default='None')

    # Slug for SEO-friendly URLs
    slug = models.SlugField(null=False, unique=True)

    # Status and Variants
    status = models.CharField(max_length=10, choices=STATUS)
    variant = models.CharField(max_length=20, choices=VARIANTS, default='None')

    # Visit Tracking
    num_of_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)

    # Diamond Specific Fields

    METAL_TYPE_CHOICES = (
        ('10kt White Gold', '10kt White Gold'),
        ('14kt Yellow Gold', '14kt Yellow Gold'),
        ('18kt Rose Gold', '18kt Rose Gold'),
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
        ('1/2 Ct.t.w.', '1/2 Ct.t.w.'),
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
## method to create a fake table field in read only mode
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return "" 

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

    def __str__(self):
        return self.title

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
    def __str__(self):
        return self.subject

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate','email','name']

