
from oscar.core.loading import is_model_registered
from apps.catalogue.abstract_models import AbstractBrand, AbstractSeries, AbstractProductActiveOptions
from django.db import models
    
__all__ = ["ProductAttributesContainer"]

if not is_model_registered("catalogue", "Series"):
    class Series(AbstractSeries):
        pass
    __all__.append("Series")
    
if not is_model_registered("catalogue", "Brand"):
    class Brand(AbstractBrand):
        pass
    __all__.append("Brand")

if not is_model_registered("catalogue", "ProductActiveOptions"):
    class ProductActiveOptions(AbstractProductActiveOptions):
        pass
    __all__.append("ProductActiveOptions")

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductImage

class Product(AbstractProduct):
    
    series = models.ForeignKey(
        'catalogue.Series',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    brand = models.ForeignKey(
        'catalogue.Brand', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="products"
    )
    
    @property
    def options(self):
        option_ids = self.product_active_options.values_list('option_id', flat=True)
        return self.get_product_class().options.filter(id__in=option_ids).distinct()
    
    def get_choices(self, option):
        """
        Возвращает список кортежей (значение, отображение) для AttributeOption,
        заданных у этого продукта для конкретной Option.
        """
        attrs = self.product_active_options.select_related("attribute_option").filter(option=option)

        # Только уникальные AttributeOption'ы
        unique_attrs = {attr.attribute_option for attr in attrs}

        choices = [(opt, opt.option) for opt in unique_attrs]

        if not option.required:
            choices = [("", "---")] + choices

        return choices

class ProductImage(AbstractProductImage):
    
    external_url = models.URLField(blank=True, null=True)
    
    option_value = models.ForeignKey(
        "catalogue.AttributeOption",  # или твоя модель значений опций
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
        help_text="Если изображение связано с определённой опцией (например, цветом)"
    )

from oscar.apps.catalogue.models import *  # noqa: F403