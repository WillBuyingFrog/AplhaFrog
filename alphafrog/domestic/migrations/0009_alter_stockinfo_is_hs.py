# Generated by Django 5.0.3 on 2024-04-11 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic', '0008_alter_stockinfo_area_alter_stockinfo_enname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinfo',
            name='is_hs',
            field=models.CharField(max_length=1, null=True),
        ),
    ]
