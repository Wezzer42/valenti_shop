import csv
from apps.catalogue.models import ProductClass, ProductAttribute

# Укажи путь к CSV или можно напрямую вставить список словарей
DEFINITION_TABLE = [
    {"definition_id": "APPLICABLE_SEASON", "cn_key": "适用季节", "ru_key": "Сезон"},
    {"definition_id": "CLOTHES_LENGTH", "cn_key": "衣长", "ru_key": "Длина одежды"},
    {"definition_id": "FABRIC", "cn_key": "面料", "ru_key": "Ткань"},
    {"definition_id": "INGREDIENTS", "cn_key": "成分含量", "ru_key": "Состав"},
    {"definition_id": "MAIN_ARTICLE_NUMBER", "cn_key": "主货号", "ru_key": "Основной номер товара"},
    {"definition_id": "RELEASE_DATE", "cn_key": "发售日期", "ru_key": "Дата выхода"},
    {"definition_id": "SALE_PRICE", "cn_key": "发售价格", "ru_key": "Цена предложения"},
    {"definition_id": "SHAPE", "cn_key": "款式", "ru_key": "Стиль"},
    {"definition_id": "SLEEVE_LENGTH", "cn_key": "袖长", "ru_key": "Длина рукава"},
    {"definition_id": "STYLE", "cn_key": "风格", "ru_key": "Стиль"},
    {"definition_id": "THICKNESS", "cn_key": "厚度", "ru_key": "Толщина"},
    {"definition_id": "VERSION", "cn_key": "版型", "ru_key": "Версия"},
    {"definition_id": "FUNCTION", "cn_key": "功能", "ru_key": "Функция"},
    {"definition_id": "PRODUCT_COUNTRY_VERSION", "cn_key": "商品国别版本", "ru_key": "Версия продукта в стране"},
    {"definition_id": "PATTERN", "cn_key": "图案", "ru_key": "Шаблон"},
    {"definition_id": "FILLING", "cn_key": "填充物", "ru_key": "Наполнитель"},
    {"definition_id": "CUSTOM_MODEL", "cn_key": "定制款", "ru_key": "Индивидуальная модель"},
    {"definition_id": "ELASTICITY", "cn_key": "弹力", "ru_key": "Эластичность"},
    {"definition_id": "WITH_FLEECE", "cn_key": "是否加绒", "ru_key": "С подкладкой"},
    {"definition_id": "QUICK_DRYING", "cn_key": "是否速干", "ru_key": "Быстросохнущий"},
    {"definition_id": "DECOR", "cn_key": "流行元素", "ru_key": "Декор"},
    {"definition_id": "PLACE_OF_ORIGIN", "cn_key": "生产产地", "ru_key": "Место производства"},
    {"definition_id": "BOOT_HEIGHT", "cn_key": "筒高", "ru_key": "Высота голенища"},
    {"definition_id": "WAIST_TYPE", "cn_key": "腰型", "ru_key": "Тип талии"},
    {"definition_id": "PLACKET", "cn_key": "衣门襟", "ru_key": "Планка (застежка)"},
    {"definition_id": "SLEEVE_TYPE", "cn_key": "袖型", "ru_key": "Тип рукава"},
    {"definition_id": "PANTS_LENGTH", "cn_key": "裤长", "ru_key": "Длина брюк"},
    {"definition_id": "PANTS_PLACKET", "cn_key": "裤门襟", "ru_key": "Ширинка"},
    {"definition_id": "SOCCER_UNIFORM_VERSION", "cn_key": "足球服版本", "ru_key": "Версия футбольной формы"},
    {"definition_id": "SECONDARY_ARTICLE_NUMBER", "cn_key": "辅助货号", "ru_key": "Вспомогательный артикул"},
    {"definition_id": "COLLAR_TYPE", "cn_key": "领型", "ru_key": "Тип воротника"},
]

# Название продукт-класса
product_class_name = "Nike Одежда"
product_class = ProductClass.objects.get(name=product_class_name)

for row in DEFINITION_TABLE:
    attr, created = ProductAttribute.objects.get_or_create(
        product_class=product_class,
        code=row["definition_id"],
        defaults={
            "name": row["ru_key"],
            "name_zh_hans": row["cn_key"],
            "type": "text",
        }
    )
    if created:
        print(f"✅ Добавлен атрибут: {row['definition_id']}")
    else:
        print(f"⚠️ Уже существует: {row['definition_id']}")