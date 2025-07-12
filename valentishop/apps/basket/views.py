from oscar.apps.basket import views as base_views
from django.contrib import messages
from django.contrib.sessions.serializers import JSONSerializer
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from oscar.core.utils import redirect_to_referrer, safe_referrer
from oscar.core.loading import get_class, get_model

BasketMessageGenerator = get_class("basket.utils", "BasketMessageGenerator")


class BasketAddView(base_views.BasketAddView):
    """
    Handles the add-to-basket submissions, which are triggered from various
    parts of the site. The add-to-basket form is loaded into templates using
    a templatetag from :py:mod:`oscar.templatetags.basket_tags`.
    """

    def form_invalid(self, form):
        msgs = []
        for error in form.errors.values():
            msgs.append(error.as_text())
        clean_msgs = [m.replace("* ", "") for m in msgs if m.startswith("* ")]
        messages.error(self.request, ",".join(clean_msgs))

        # We serialize the POST data with JSONSerializer before adding it to the session.
        # Without this, we could expose the site to a security vulnerability
        # if the SESSION_SERIALIZER has been configured to 'django.contrib.sessions.serializers.PickleSerializer'.
        # see: https://docs.djangoproject.com/en/3.2/topics/http/sessions/#cookie-session-backend
        serialized_data = JSONSerializer().dumps(self.request.POST)
        self.request.session["add_to_basket_form_post_data_%s" % self.product.pk] = (
            serialized_data.decode("latin-1")
        )

        return redirect_to_referrer(self.request, "basket:summary")

    def form_valid(self, form):
        if 'buy_now' in self.request.POST:
            if not self.request.user.is_authenticated:
                messages.warning(self.request, "Пожалуйста, авторизуйтесь для оформления заказа.")
                return HttpResponseRedirect(self.get_success_url())
            saved_basket, _ = get_model("basket", "basket").saved.get_or_create(owner=self.request.user)
            # Перемещаем всё в SavedBasket
            for line in self.request.basket.all_lines():
                saved_basket.merge_line(line)
        
        offers_before = self.request.basket.applied_offers()

        self.request.basket.add_product(
            form.product, form.cleaned_data["quantity"], form.cleaned_options()
        )
        if not 'buy_now' in self.request.POST:
            # Check for additional offer messages
            BasketMessageGenerator().apply_messages(self.request, offers_before)

        # Send signal for basket addition
        self.add_signal.send(
            sender=self,
            product=form.product,
            user=self.request.user,
            request=self.request,
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        post_url = self.request.POST.get("next")
        if post_url and url_has_allowed_host_and_scheme(
            post_url, self.request.get_host()
        ):
            return post_url
        return safe_referrer(self.request, "basket:summary")