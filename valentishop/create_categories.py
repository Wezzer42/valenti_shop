import os
import re
from django.utils.text import slugify
from oscar.core.loading import get_model

Category = get_model("catalogue", "category")

CATEGORY_FILE = "category3_list.txt"

CATEGORY_TRANSLATIONS = {
    "footwear": "Обувь",
    "sport": "Спорт",
    "running": "Беговые",
    "casual": "Повседневные",
    "sneakers": "Кроссовки",
    "canvas": "Тканевые",
    "vintage_basketball": "Ретро баскетбол",
    "daddy": "Папины",
    "training": "Тренировочные",
    "soccer": "Футбольные",
    "badminton": "Бадминтон",
    "tennis": "Теннис",
    "golf": "Гольф",
    "cycling": "Велоспорт",
    "boots": "Ботинки",
    "martin": "Мартинсы",
    "outdoor": "Трекинговые",
    "short": "Короткие",
    "chelsea": "Челси",
    "snow": "Зимние",
    "slippers": "Сланцы",
    "flip_flops": "Шлёпанцы",
    "sport_sandals": "Спортивные сандалии",
    "apparel": "Одежда",
    "featured_tops": "Верхняя одежда",
    "t_shirt": "Футболки",
    "hoodie": "Худи",
    "shirt": "Рубашки",
    "polo_shirt": "Поло",
    "sweater": "Свитера",
    "vest": "Жилеты",
    "featured_jacket": "Куртки",
    "jacket": "Куртка",
    "jackets": "Куртки",
    "down_jacket": "Пуховики",
    "cotton_clothes": "Хлопковые куртки",
    "sun_protection": "От солнца",
    "denim_jacket": "Джинсовка",
    "windbreaker": "Ветровка",
    "leather_jacket": "Кожаная куртка",
    "coat": "Пальто",
    "suit": "Костюм",
    "baseball_uniform": "Бейсбольная куртка",
    "pants": "Штаны",
    "jeans": "Джинсы",
    "casual_shorts": "Повседневные шорты",
    "denim_short": "Джинсовые шорты",
    "underwear": "Нижнее белье",
    "overralls2": "Комбинезоны",
    "overalls": "Комбинезоны",
    "workout": "Тренировочная одежда",
    "workout_pants": "Спортивные штаны",
    "basketball_pants": "Баскетбольные штаны",
    "basketball_vest": "Баскетбольная майка",
    "workout_clothes": "Форма",
    "ski_suit": "Лыжный костюм",
    "ski_pants": "Лыжные штаны",
    "lingerie": "Белье",
    "socks": "Носки",
    "panties": "Трусы",
    "accessories": "Аксессуары",
    "bags": "Сумки",
    "underarm_bag": "Сумка под мышку",
    "tote": "Шоппер",
    "backpack": "Рюкзак",
    "diagonal_bag": "Сумка через плечо",
    "fanny_pack": "Поясная сумка",
    "wallet": "Кошелёк",
    "chest_bag": "Нагрудная сумка",
    "card_holder": "Кардхолдер",
    "coin_purse": "Монетница",
    "gym_bag": "Спортивная сумка",
    "mobile_phone_bag": "Сумка для телефона",
    "brief_case": "Портфель",
    "makeup_bag": "Косметичка",
    "wash_bag": "Несессер",
    "bags_accessories": "Аксессуары к сумкам",
    "bag_peripheral": "Фурнитура для сумок",
    "tape": "Ленты",
    "hat": "Головные уборы",
    "peaked_cap": "Кепка",
    "fleece": "Флисовая шапка",
    "fisherman": "Панамка",
    "berets": "Берет",
    "other": "Другое",
    "hair_accessories": "Аксессуары для волос",
    "hairpin": "Заколка",
    "headband": "Ободок",
    "children_headband": "Детский ободок",
    "glasses": "Очки",
    "sunglasses": "Солнцезащитные очки",
    "optical_frame": "Оправа",
    "scarf": "Шарфы",
    "silk": "Шёлковый шарф",
    "belt": "Ремни",
    "jewelry": "Украшения",
    "necklace": "Ожерелье",
    "bracelet": "Браслет",
    "bracelet2": "Браслет 2",
    "earning": "Серьги",
    "ring": "Кольцо",
    "pendant": "Кулон",
    "wristband": "Напульсник",
    "key_chain": "Брелок",
    "watch": "Часы",
    "mechanical": "Механические",
    "quartz": "Кварцевые",
    "alarm_clock": "Будильник",
    "face_mask": "Маска",
    "brooch": "Брошь"
}

def create_from_sequence_en(parts_en):
    """
    parts_en: список на английском (например ["footwear", "casual", "sneakers"])
    Создаёт категории и возвращает последнюю
    """
    parent = None
    for part in parts_en:
        slug = slugify(part)
        name_en = part.replace("_", " ").capitalize()

        # Проверка существования
        if parent is None:
            qs = Category.objects.filter(depth=1, slug=slug)
        else:
            qs = parent.get_children().filter(slug=slug)

        if qs.exists():
            category = qs.first()
        else:
            if parent is None:
                category = Category.add_root(name=name_en, slug=slug)
            else:
                category = parent.add_child(name=name_en, slug=slug)

        # Устанавливаем name_en, если пусто
        if not category.name_en:
            category.name_en = name_en

        # Обновим name (русский), если есть перевод
        translated = CATEGORY_TRANSLATIONS.get(part)
        if translated and category.name != translated:
            category.name = translated

        category.save()
        parent = category

    return category


# 🚀 Основной запуск
with open(CATEGORY_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    if not line.strip():
        continue
    raw = re.split(r"\s+\(\d+\)", line)[0].strip()
    parts = raw.split("/")
    create_from_sequence_en(parts)

print("✅ Категории созданы: английская структура + русская локализация.")
