# Generated by Django 5.1.5 on 2025-02-14 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ewallet', '0002_alter_wallet_wallet_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='wallet_number',
            field=models.CharField(default='', max_length=20, unique=True),
        ),
    ]
