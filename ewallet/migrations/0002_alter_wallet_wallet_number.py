# Generated by Django 5.1.5 on 2025-02-17 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewallet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='wallet_number',
            field=models.CharField(editable=False, max_length=10, unique=True),
        ),
    ]
