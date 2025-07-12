from oscar.apps.basket import forms as base_forms
from django import forms
from apps.forms import widgets
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from oscar.core.loading import get_model

Option = get_model("catalogue", "option")


def _option_text_field(form, product, option):
    return forms.CharField(
        label=option.name, required=option.required, help_text=option.help_text
    )


def _option_integer_field(form, product, option):
    return forms.IntegerField(
        label=option.name, required=option.required, help_text=option.help_text
    )


def _option_boolean_field(form, product, option):
    return forms.BooleanField(
        label=option.name, required=option.required, help_text=option.help_text
    )


def _option_float_field(form, product, option):
    return forms.FloatField(
        label=option.name, required=option.required, help_text=option.help_text
    )


def _option_date_field(form, product, option):
    return forms.DateField(
        label=option.name,
        required=option.required,
        widget=forms.widgets.SelectDateWidget,
        help_text=option.help_text,
    )

def _option_select_field(form, product, option):
    return forms.ChoiceField(
        label=option.name,
        required=option.required,
        choices=product.get_choices(option),
        help_text=option.help_text,
    )


def _option_radio_field(form, product, option):
    return forms.ChoiceField(
        label=option.name,
        required=option.required,
        choices=product.get_choices(option),
        widget=forms.RadioSelect,
        help_text=option.help_text,
    )


def _option_multi_select_field(form, product, option):
    return forms.MultipleChoiceField(
        label=option.name,
        required=option.required,
        choices=product.get_choices(option),
        help_text=option.help_text,
    )


def _option_checkbox_field(form, product, option):
    return forms.MultipleChoiceField(
        label=option.name,
        required=option.required,
        choices=product.get_choices(option),
        widget=forms.CheckboxSelectMultiple,
        help_text=option.help_text,
    )

class AddToBasketForm(base_forms.AddToBasketForm):
    OPTION_FIELD_FACTORIES = {
        Option.TEXT: _option_text_field,
        Option.INTEGER: _option_integer_field,
        Option.BOOLEAN: _option_boolean_field,
        Option.FLOAT: _option_float_field,
        Option.DATE: _option_date_field,
        Option.SELECT: _option_select_field,
        Option.RADIO: _option_radio_field,
        Option.MULTI_SELECT: _option_multi_select_field,
        Option.CHECKBOX: _option_checkbox_field,
    }

    def _create_parent_product_fields(self, product):
        """
        Adds the fields for a "group"-type product (eg, a parent product with a
        list of children.

        Currently requires that a stock record exists for the children
        """
        choices = []
        disabled_values = []
        prices = {}
        parent_info = self.basket.strategy.fetch_for_product(product)
        selected_stockrecord = parent_info.stockrecord
        initial_child_id = None
        
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
            summary = format_html(r'<strong class="text-sm sm:text-base">{}</strong><span class="text-[10px] sm:text-xs text-gray-500">{}</span>', child.title, formatted_price)

            # Проверяем доступность товара для покупки
            if not info.availability.is_available_to_buy:
                disabled_values.append(child.id)

            choices.append((child.id, summary))
            prices[child.id] = price
            if selected_stockrecord and info.stockrecord:
                if selected_stockrecord.id == info.stockrecord.id:
                    initial_child_id = str(child.id)

        self.fields["child_id"] = forms.ChoiceField(
            choices=tuple(choices),
            label=_("Sizes:"),
            widget=widgets.AdvancedRadioSelect(disabled_values=disabled_values),
            initial=initial_child_id,
        )


class SimpleAddToBasketForm(base_forms.SimpleAddToBasketMixin, AddToBasketForm):
    pass
