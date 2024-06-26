# Generated by Django 5.0.6 on 2024-06-05 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_alter_category_violator'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_kg',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='violator',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='violator',
            name='name_kg',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='violator',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
