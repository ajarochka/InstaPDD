# Generated by Django 5.0.6 on 2024-06-15 18:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0017_postmedia_delete_postimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postmedia',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='post.post', verbose_name='Post'),
        ),
    ]
