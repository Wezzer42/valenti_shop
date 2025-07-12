from django import forms
from django.utils.encoding import force_str
from django.conf import settings


class AdvancedRadioSelect(forms.RadioSelect):

    template_name = "widgets/radio.html"
    """
    Customised Select widget that allows a list of disabled values to be passed
    to the constructor.  Django's default Select widget doesn't allow this so
    we have to override the render_option method and add a section that checks
    for whether the widget is disabled.
    """

    def __init__(self, attrs=None, choices=(), disabled_values=()):
        self.disabled_values = set(force_str(v) for v in disabled_values)
        super().__init__(attrs, choices)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if force_str(value) in self.disabled_values:
            option["attrs"]["disabled"] = True
        option["selected"] = selected
        return option
