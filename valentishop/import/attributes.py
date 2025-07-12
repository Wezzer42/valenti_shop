import os
import csv
from transliterate import translit

from oscar.apps.catalogue.models import (
    ProductAttribute, ProductAttributeValue,
    AttributeOptionGroup, AttributeOption
)

TRANSLATION_DIR = "translations/attributes"

FORCE_MULTI_OPTION = {
    "APPLICABLE_PLAY_STYLE", "APPLICABLE_SCENE", "APPLICABLE_SEASON", "APPLICABLE_VENUES",
    "CLOSURE", "CLOTHES_LENGTH", "FABRIC", "FEATURE", "HEEL_TYPE", "MATERIAL", "PRIMARY_COLOR",
    "PRODUCT_HEIGHT", "PRODUCT_IMAGE", "SECONDARY_COLOR", "SHAPE", "SLEEVE_LENGHT", "STYLE",
    "THICKNESS", "TOE_STYLE", "UPPER_HEIGHT", "UPPER_MATERIAL", "VERSION",
    "FIT", "SIZE_TABLE"
}


def assign_attributes_from_poizon_data(product, data):
    product_class = product.get_product_class()

    # 1. fit
    fit_val = data.get("fit")
    if fit_val:
        _assign_option(product, "FIT", "Пол / возраст", "FIT", [fit_val.strip()])

    # 2. spuId
    spu_id = data.get("spuId")
    if spu_id:
        _assign_text(product, "spuId", "SPU ID", "SPU ID", str(spu_id))

    # 3. sizeTable
    # 3. sizeTable
    all_systems = []

    for size_table in data.get("sizeTable", []):
        system = size_table.get("type")
        values = size_table.get("values", [])
        if system and values:
            all_systems.append(system)
            _assign_multi_option(product, system, f"Размеры {system}", f"{system} 尺码", values)

        if all_systems:
            _assign_multi_option(product, "SIZE_TABLE", "Системы размеров", "尺码系统", all_systems)


    # 4. productProperties
    for prop in data.get("productProperties", []):
        definition_id = prop.get("definitionId") or translit(prop.get("translatedKey", ""), "ru", reversed=True)
        original_key = prop.get("key", "")
        values = prop.get("value", [])
        translated_values = prop.get("translatedValue", [])

        if not values and not translated_values:
            continue

        translated_key, value_translations, original_key_csv = load_attribute_translation(definition_id)
        final_key = translated_key or prop.get("translatedKey") or original_key
        zh_key = original_key_csv or original_key

        # fallback переводов
        if not translated_values:
            translated_values = [value_translations.get(v, v) for v in values]

        if definition_id in FORCE_MULTI_OPTION or len(translated_values) > 1:
            _assign_multi_option(product, definition_id, final_key, zh_key, translated_values)
        else:
            _assign_text(product, definition_id, final_key, zh_key, translated_values[0])


def _assign_multi_option(product, code, name_ru, name_zh, values):
    attr, _ = ProductAttribute.objects.get_or_create(
        code=code,
        defaults={"name_ru": name_ru, "name_zh_hans": name_zh, "type": "multi_option"}
    )
    attr.name_ru = name_ru
    attr.name_zh_hans = name_zh
    attr.type = "multi_option"
    attr.save()

    if not attr.option_group:
        group = AttributeOptionGroup.objects.create(name=f"{code}-group")
        attr.option_group = group
        attr.save()
    else:
        group = attr.option_group

    for val in values:
        AttributeOption.objects.get_or_create(group=group, option=val)

    product.get_product_class().attributes.add(attr)
    pav, _ = ProductAttributeValue.objects.get_or_create(product=product, attribute=attr)
    for val in values:
        option = AttributeOption.objects.get(group=group, option=val)
        pav.value_multi_option.add(option)
    pav.save()

def _assign_option(product, code, name_ru, name_zh, values):
    attr, _ = ProductAttribute.objects.get_or_create(
        code=code,
        defaults={"name_ru": name_ru, "name_zh_hans": name_zh, "type": "multi_option"}
    )
    attr.name_ru = name_ru
    attr.name_zh_hans = name_zh
    attr.type = "option"
    attr.save()

    if not attr.option_group:
        group = AttributeOptionGroup.objects.create(name=f"{code}-group")
        attr.option_group = group
        attr.save()
    else:
        group = attr.option_group

    for val in values:
        AttributeOption.objects.get_or_create(group=group, option=val)

    product.get_product_class().attributes.add(attr)
    pav, _ = ProductAttributeValue.objects.get_or_create(product=product, attribute=attr)
    for val in values:
        option = AttributeOption.objects.get(group=group, option=val)
        pav.value_multi_option.add(option)
    pav.save()


def _assign_text(product, code, name_ru, name_zh, value):
    attr, _ = ProductAttribute.objects.get_or_create(
        code=code,
        defaults={"name_ru": name_ru, "name_zh_hans": name_zh, "type": "text"}
    )
    attr.name_ru = name_ru
    attr.name_zh_hans = name_zh
    attr.type = "text"
    attr.save()

    product.get_product_class().attributes.add(attr)
    pav, _ = ProductAttributeValue.objects.get_or_create(product=product, attribute=attr)
    pav.value_text = value
    pav.save()


def load_attribute_translation(definition_id):
    file_path = os.path.join(TRANSLATION_DIR, f"{definition_id}.csv")
    if not os.path.exists(file_path):
        return None, {}, None

    translated_key = None
    original_key = None
    value_translations = {}

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header_skipped = False
        for row in reader:
            if not header_skipped:
                header_skipped = True
                continue
            if len(row) != 2:
                continue
            key, translation = row
            if original_key is None:
                original_key = key.strip()
            if translated_key is None:
                translated_key = translation.strip()
            value_translations[key.strip()] = translation.strip()

    return translated_key, value_translations, original_key
