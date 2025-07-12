import os
import json
from django.utils.text import slugify
from django.db import transaction
from apps.catalogue.models import Product, ProductClass, Category

# Маппинг: "бренд + категория" -> слаг продукт-класса
PRODUCT_CLASS_MAPPING = {
    "Nike apparel": "nike-apparel",
    "Rabbit House apparel": "rabbit-house-apparel",
    # добавь сюда весь твой список
}

DEFAULT_CATEGORY_SLUG = "unknown"

def get_or_create_product_class(brand, category1):
    key = f"{brand} {category1}".strip()
    slug = PRODUCT_CLASS_MAPPING.get(key, f"{slugify(brand)}_unknown")
    return ProductClass.objects.get_or_create(slug=slug, defaults={"name": slug})[0]

@transaction.atomic
def create_product_from_json(data):
    article = data.get("article")
    if not article:
        print("❌ Нет артикула, пропускаем товар.")
        return

    # Проверка: есть ли продукт с таким артикулом?
    if Product.objects.filter(article=article).exists():
        print(f"⚠️ Продукт с артикулом {article} уже существует. Пропускаем.")
        return
    brand = data.get("brand", "").strip()
    category_data = data.get("category", {})
    category1 = category_data.get("category1", "").strip()

    product_class = get_or_create_product_class(brand, category1)

    product = Product.objects.create(
        title=data.get("name", ""),
        product_class=product_class,
        description=data.get("description", ""),
        slug=data.get("slug", ""),
        upc=data.get("article", ""),
    )

    # Привязка к категориям
    for i in range(1, 4):
        cat_slug = category_data.get(f"category{i}")
        if cat_slug:
            category, _ = Category.objects.get_or_create(slug=cat_slug)
        else:
            category, _ = Category.objects.get_or_create(slug=DEFAULT_CATEGORY_SLUG)
        product.categories.add(category)

    return product

def import_all_products_from_dir(directory):
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(directory, filename)
        with open(path, encoding="utf-8") as f:
            try:
                data = json.load(f)
                create_product_from_json(data)
                print(f"✅ Imported: {filename}")
            except Exception as e:
                print(f"❌ Failed {filename}: {e}")