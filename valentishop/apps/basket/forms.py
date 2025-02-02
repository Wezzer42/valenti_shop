from oscar.apps.basket import forms as base_forms
from django import forms
from apps.forms import widgets
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


class AddToBasketForm(base_forms.AddToBasketForm):

    def _create_parent_product_fields(self, product):
        """
        Adds the fields for a "group"-type product (eg, a parent product with a
        list of children.

        Currently requires that a stock record exists for the children
        """
        choices = []
        disabled_values = []
        prices = {}
        for child in product.children.public():
            # Получаем информацию о наличии и цене для каждого дочернего продукта
            info = self.basket.strategy.fetch_for_product(child)
            price = info.price.incl_tax if info.price else None  # Получаем цену с налогом

            # Формируем строку с отображением цены и валюты через фильтр currency
            if price:
                # Создаем строку для фильтра

                formatted_price = f"{price} ₽"
            else:
                formatted_price = "--"

            # Составляем описание дочернего продукта
            summary = format_html("<strong>{}</strong><br>{}", child.title, formatted_price)

            # Проверяем доступность товара для покупки
            if not info.availability.is_available_to_buy:
                disabled_values.append(child.id)

            choices.append((child.id, summary))
            prices[child.id] = price

        self.fields["child_id"] = forms.ChoiceField(
            choices=tuple(choices),
            label=_("Sizes"),
            widget=widgets.AdvancedRadioSelect(disabled_values=disabled_values),
        )


class SimpleAddToBasketForm(base_forms.SimpleAddToBasketMixin, AddToBasketForm):
    pass
