from oscar.apps.partner.strategy import StockRequired as BaseStockRequired
from oscar.apps.partner.strategy import NoTax as BaseNoTax
from oscar.apps.partner.strategy import Selector as BaseSelector
from oscar.apps.partner.strategy import UseFirstStockRecord, Structured
from oscar.core.loading import get_class
from decimal import Decimal as D

Unavailable = get_class("partner.availability", "Unavailable")
Available = get_class("partner.availability", "Available")
StockRequiredAvailability = get_class("partner.availability", "StockRequired")
UnavailablePrice = get_class("partner.prices", "Unavailable")
FixedPrice = get_class("partner.prices", "FixedPrice")


class Selector(BaseSelector):
    """
    Responsible for returning the appropriate strategy class for a given
    user/session.

    This can be called in three ways:

    #) Passing a request and user. This is for determining
       prices/availability for a normal user browsing the site.

    #) Passing just the user. This is for offline processes that don't
       have a request instance but do know which user to determine prices for.

    #) Passing nothing. This is for offline processes that don't
       correspond to a specific user, e.g., determining a price to store in
       a search index.

    """

    # pylint: disable=unused-argument
    def strategy(self, request=None, user=None, **kwargs):
        """
        Return an instantiated strategy instance
        """
        # Default to the backwards-compatible strategy of picking the first
        # stockrecord but charging zero tax.
        return Default(request)


class StockRequired(BaseStockRequired):
    """
    Availability policy mixin for use with the ``Structured`` base strategy.
    This mixin ensures that a product can only be bought if it has stock
    available (if stock is being tracked).
    """

    def availability_policy(self, product, stockrecord):
        if not stockrecord or stockrecord.price == None:
            return Unavailable()
        if not product.get_product_class().track_stock:
            return Available()
        else:
            return StockRequiredAvailability(stockrecord.net_stock_level)

    def parent_availability_policy(self, product, children_stock):
        # A parent product is available if one of its children is
        for child, stockrecord in children_stock:
            policy = self.availability_policy(child, stockrecord)
            if policy.is_available_to_buy:
                return Available()
        return Unavailable()
    

class NoTax(BaseNoTax):
    """
    Pricing policy mixin for use with the ``Structured`` base strategy.
    This mixin specifies zero tax and uses the ``price`` from the
    stockrecord.
    """

    def pricing_policy(self, product, stockrecord):
        # Check stockrecord has the appropriate data
        if not stockrecord or stockrecord.price is None:
            return UnavailablePrice()
        return FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price,
            tax=D("0.00"),
        )

    def parent_pricing_policy(self, product, children_stock):
        stockrecords = [x[1] for x in children_stock if x[1].price is not None]
        if not stockrecords:
            return UnavailablePrice()
        # We take price from first record
        stockrecord = stockrecords[0]
        return FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price,
            tax=D("0.00"),
        )


class Default(UseFirstStockRecord, StockRequired, NoTax, Structured):
    """
    Default stock/price strategy that uses the first found stockrecord for a
    product, ensures that stock is available (unless the product class
    indicates that we don't need to track stock) and charges zero tax.
    """