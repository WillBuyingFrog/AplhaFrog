# Generated by Django 5.0.3 on 2024-04-11 09:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic', '0005_indexcomponentweight_con_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockinfo',
            name='index_component_weights',
            field=models.ManyToManyField(related_name='stock_infos', to='domestic.indexcomponentweight'),
        ),
        migrations.AlterField(
            model_name='indexcomponentweight',
            name='con_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='domestic.stockinfo'),
        ),
    ]
