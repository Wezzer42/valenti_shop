from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView


class ProductDetailView(CoreProductDetailView):
    enforce_parent = True
