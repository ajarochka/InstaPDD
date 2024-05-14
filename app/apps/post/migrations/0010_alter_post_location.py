# Generated by Django 5.0.6 on 2024-05-14 16:41

import apps.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0009_post_location_alter_post_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='location',
            field=apps.core.fields.OSMPointField(null=True, srid=4326),
        ),
    ]
