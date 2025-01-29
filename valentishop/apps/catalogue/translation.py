from modeltranslation.translator import translator, TranslationOptions
from .models import Category


class NewsTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(Category, NewsTranslationOptions)
