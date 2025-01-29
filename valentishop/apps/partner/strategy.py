from oscar.apps.partner import strategy as strategy


class NoTax(strategy.NoTax):

    def pricing_policy(self, product, stockrecord):
        # Check stockrecord has the appropriate data
        if not stockrecord or stockrecord.price is None or stockrecord.price==0:
            return strategy.UnavailablePrice()
        return strategy.FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price,
            tax=strategy.D("0.00"),
        )
    
    def parent_pricing_policy(self, product, children_stock):
        stockrecords = [x[1] for x in children_stock if x[1] is not None or x[1]!=0]
        if not stockrecords:
            return strategy.UnavailablePrice()
        # We take price from first record
        stockrecord = stockrecords[0]
        return strategy.FixedPrice(
            currency=stockrecord.price_currency,
            excl_tax=stockrecord.price,
            tax=strategy.D("0.00"),
        )