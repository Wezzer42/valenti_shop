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
            # Build a description of the child, including any pertinent
            # attributes
            
            
            # Check if it is available to buy
            info = self.basket.strategy.fetch_for_product(child)
            price = info.price.incl_tax if info.price else None  # Получаем цену
            summary = format_html("{}<br><strong>${}</strong>", child.title, price) if price else format_html("{}<br><strong>{}</strong>", child.title, "--")
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
