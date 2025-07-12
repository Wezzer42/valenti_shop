from modeltranslation.translator import translator, TranslationOptions
from modeltranslation.translator import register, TranslationOptions
from apps.catalogue.models import (
    ProductAttribute, ProductAttributeValue,
    Option, AttributeOption, AttributeOptionGroup, Category
)

@register(ProductAttribute)
class ProductAttributeTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ProductAttributeValue)
class ProductAttributeValueTranslationOptions(TranslationOptions):
    fields = ('value_text',)

@register(Option)
class OptionTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(AttributeOption)
class AttributeOptionTranslationOptions(TranslationOptions):
    fields = ('option',)

@register(AttributeOptionGroup)
class AttributeOptionGroupTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
