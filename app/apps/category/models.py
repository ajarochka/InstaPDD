from django.db import models

# Create your models here.

class Violator(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    violator = models.ForeignKey(Violator, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

