from oscar.apps.catalogue.models import ProductClass

with open("product_classes.txt", "r", encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name:
            ProductClass.objects.get_or_create(
                name=name,
                defaults={"track_stock": False}
            )