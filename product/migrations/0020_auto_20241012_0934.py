# Generated by Django 3.0.7 on 2024-10-12 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0019_auto_20241012_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='carats_total_weight',
            field=models.CharField(choices=[('1/2 Ct.t.w.', '1/2 Ct.t.w.'), ('1 Ct.t.w.', '1 Ct.t.w.'), ('1.25 Ct.t.w.', '1.25 Ct.t.w.'), ('1.5 Ct.t.w.', '1.5 Ct.t.w.'), ('1.75 Ct.t.w.', '1.75 Ct.t.w.'), ('2 Ct.t.w.', '2 Ct.t.w.'), ('2.25 Ct.t.w.', '2.25 Ct.t.w.'), ('2.5 Ct.t.w.', '2.5 Ct.t.w.'), ('2.75 Ct.t.w.', '2.75 Ct.t.w.'), ('3 Ct.t.w.', '3 Ct.t.w.'), ('3.25 Ct.t.w.', '3.25 Ct.t.w.'), ('3.5 Ct.t.w.', '3.5 Ct.t.w.'), ('3.75 Ct.t.w.', '3.75 Ct.t.w.'), ('4 Ct.t.w.', '4 Ct.t.w.'), ('4.25 Ct.t.w.', '4.25 Ct.t.w.'), ('4.5 Ct.t.w.', '4.5 Ct.t.w')], default='1/2 Ct.t.w.', max_length=20),
        ),
    ]
