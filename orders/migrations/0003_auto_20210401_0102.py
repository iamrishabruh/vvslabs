# Generated by Django 3.1.7 on 2021-03-31 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_orderproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_one',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_two',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='code',
            field=models.CharField(editable=False, max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='country',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='email',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='first_name',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_name',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='order',
            name='postal_code',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
