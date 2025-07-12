import os
import json
from apps.catalogue.models import Product, ProductAttributeValue, AttributeOption, ProductClass, ProductImage
from oscar.apps.catalogue.models import Category, ProductCategory
from django.utils.text import slugify

BASE_DIR = "/home/azat/Projects/parserpoizon"

def create_parent_product(data):
    # Категория
    try:
        category_name = data["category"]["category3"].split("/")[-1]
    except KeyError:
        try:
            category_name = data["category"]["category2"].split("/")[-1]
        except KeyError:
            category_name = data["category"]["category1"]

    category = Category.objects.filter(name=category_name).first()
    if not category:
        print(f"Категория '{category_name}' не найдена")
        return

    # Продукт-класс
    product_class = ProductClass.objects.get(slug=data["category"]["category1"])

    # Создание продукта
    product, _ = Product.objects.get_or_create(
        upc=data["article"],
        defaults={
            "title": data["name"],
            "slug": data["slug"],
            "description": data.get("description", ""),
            "structure": "parent",
            "product_class": product_class,
        }
    )

    # Связь с категорией
    ProductCategory.objects.get_or_create(product=product, category=category)

    # Связь с брендом через Category
    brand_category, _ = Category.objects.get_or_create(name=data["brand"])
    ProductCategory.objects.get_or_create(product=product, category=brand_category)

    # Добавляем атрибут fit (если он есть)
    if data.get("fit"):
        fit_option, _ = AttributeOption.objects.get_or_create(option=data['fit'], group=fit_group)
        ProductAttributeValue.objects.get_or_create(product=product, attribute=fit, value_option=fit_option)

    # Добавляем атрибут SPU
    ProductAttributeValue.objects.get_or_create(product=product, attribute=spu, value_integer=data["spuId"])

    # Добавляем изображения
    for i, url in enumerate(data.get("images", [])):
        ProductImage.objects.get_or_create(
            product=product,
            external_url=url,
            display_order=i
        )

    print(f"Создан родительский продукт: {product.title} / SPU: {data['spuId']}")
    return product


BASE_DIR = "/home/azat/Projects/parserpoizon"

for brand_name in os.listdir(BASE_DIR):
    brand_path = os.path.join(BASE_DIR, brand_name)
    if not os.path.isdir(brand_path):
        continue

    for filename in os.listdir(brand_path):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(brand_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Ошибка в файле: {file_path}")
            continue

        # ⬇⬇⬇ Здесь вставляешь логику создания товара
        print(f"Загружаем товар: {data['name']} от бренда {brand_name}")