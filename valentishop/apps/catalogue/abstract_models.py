from django.db import models
from django.utils.translation import gettext_lazy as _

class AbstractBrand(models.Model):
    name = models.CharField(_("Название"), max_length=255, unique=True)
    slug = models.SlugField(_("Слаг"), max_length=255, unique=True)
    logo = models.ImageField(_("Логотип"), upload_to="brands/logos/", blank=True, null=True)
    description = models.TextField(_("Описание"), blank=True)
    is_active = models.BooleanField(_("Активен"), default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = _("Бренд")
        verbose_name_plural = _("Бренды")
        ordering = ['name']

    def __str__(self):
        return self.name
    
class AbstractSeries(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='series_images/', blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _("Серия")
        verbose_name_plural = _("Серии")
        ordering = ['name']

    def __str__(self):
        return self.name
    

class AbstractProductActiveOptions(models.Model):
    product = models.ForeignKey(
        'catalogue.Product',
        on_delete=models.CASCADE,
        related_name='product_active_options',
        verbose_name="Продукт"
    )
    option = models.ForeignKey(
        'catalogue.Option',
        on_delete=models.CASCADE,
        verbose_name="Опция"
    )
    attribute_option = models.ForeignKey(
        'catalogue.AttributeOption',
        on_delete=models.CASCADE,
        verbose_name="Значение опции"
    )

    class Meta:
        abstract = True
        unique_together = ('product', 'option', 'attribute_option')
        verbose_name = "Опция продукта"
        verbose_name_plural = "Опции продукта"

    def __str__(self):
        return f"{self.product} — {self.option.name}: {self.attribute_option.option}"
    
from oscar.apps.catalogue.abstract_models import *