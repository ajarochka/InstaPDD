from modeltranslation.translator import translator, TranslationOptions
from .models import Violator, Category


class ViolatorTranslationOptions(TranslationOptions):
    fields = ('name',)



class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Violator, ViolatorTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
