import json
import requests
import os
from datetime import datetime
from transliterate import translit
import boto3
from botocore import exceptions


from oscar.apps.catalogue.models import Product, Category, ProductAttribute, \
    ProductClass, ProductCategory, \
    ProductAttributeValue, AttributeOptionGroup, AttributeOption, \
    ProductImage
from oscar.apps.partner.models import Partner, StockRecord
import logging
from django.core.files import File

logger = logging.getLogger(__name__)
logging.basicConfig(filename="import_products_log.txt", level=logging.INFO)

partner = Partner.objects.get_or_create(name="Valentine")[0]
partner.save()
product_class = ProductClass.objects.get_or_create(name='Обувь', slug='footwear', track_stock=False)[0]
cny_price = ProductAttribute.objects.get_or_create(name='Цены Китая', product_class=product_class, code="cnyPrice", type="integer")[0]
product_class.save()
spu = ProductAttribute.objects.get_or_create(name='Идентификатор товара Poizon', product_class=product_class, code="spuId", type="integer")[0]
spu.save()
fit_group = AttributeOptionGroup.objects.get_or_create(name='Посадка')[0]
fit_group.save()
fit = ProductAttribute.objects.get_or_create(name='Посадка', product_class=product_class, code="fit", type="option", option_group=fit_group)[0]
fit.save()
j = 1
for i in range(11):
    file = open("/home/azat/Projects/parserpoizon/sneakers" + str(i + 1) + ".json", "r")
    temp_data = json.load(file)
    for item in temp_data['items']:
        with open('/home/azat/Projects/parserpoizon/' + item['brand'] + '/' + str(item['spuId']) + '.json', 'r') as f:
            ch_atrr = []
            ch_atrr_op = []
            skus = {}
            skus_data = []
            data = json.load(f)
            if Product.objects.filter(upc=data['article']).exists() and j <= 194:
                print(data['article'] + str(j))
                if j >= 194:
                    Product.objects.get_or_create(upc=data['article'])[0].save()
                j += 1
                continue
            if data['category']['category1'] == str(product_class.slug):
                product = Product.objects.get_or_create(upc=data['article'], title=data['name'], product_class=product_class, description=data['description'], structure='parent')[0]
                try:
                    category = Category.objects.filter(name=data['category']['category3'].split("/")[-1])[0]
                except KeyError:
                    logger.info("Товар " + data['name'] + " SPU: " + str(data['spuId']) + '. Третий уровень категории остутствует.')
                    try:
                        category = Category.objects.filter(name=data['category']['category2'].split("/")[-1])[0]
                    except KeyError:
                        logger.info("Товар " + data['name'] + " SPU: " + str(data['spuId']) + '. Второй уровень категории остутствует.')
                        category = Category.objects.filter(name=data['category']['category1'])[0]
                product_category = ProductCategory.objects.get_or_create(category=category, product=product)[0]
                product_category.save()
                brand = Category.objects.get_or_create(name=data["brand"])[0]
                product_category = ProductCategory.objects.get_or_create(category=brand, product=product)[0]
                product_category.save()
                fit_option = AttributeOption.objects.get_or_create(option=data['fit'], group=fit_group)[0]
                fit_option.save()
                product_att_value = ProductAttributeValue.objects.get_or_create(product=product, attribute=fit, value_option=fit_option)[0]
                product_att_value.save()
                product_att_value = ProductAttributeValue.objects.get_or_create(product=product, attribute=spu, value_integer=data["spuId"])[0]
                product_att_value.save()

                for image in data["images"]:
                    if not ProductImage.objects.filter(caption=image.split('/')[-1]).exists():
                        img = requests.get(image)
                        file = open("product_images/product.jpg", 'wb+')
                        file.write(img.content)
                        product_image = ProductImage.objects.get_or_create(product=product, original=File(file), caption=image.split('/')[-1])[0]
                        file.close()
                        product_image.save()
                if len(data['properties']['propertyTypes']) > 1:
                    for property in data['properties']['propertyTypes']:

                        if property['name'] != 'Размер':
                            ch_atrr.append(property['name'])
                            for values in property["values"]:
                                ch_atrr.append(values['value'])
                            ch_atrr_op.append(ch_atrr)
                            ch_atrr = []
                        else:
                            option_group = AttributeOptionGroup.objects.get_or_create(name=property['name'])[0]
                            size = ProductAttribute.objects.get_or_create(name=property['name'], code=translit(property['name'], "ru", reversed=True), product_class=product_class, type="multi_option", option_group=option_group)[0]
                            for values in property["values"]:
                                size_option = AttributeOption.objects.get_or_create(option=values['value'], group=option_group)[0]
                                size_option.save()
                                size_value = ProductAttributeValue.objects.get_or_create(product=product, attribute=size)[0]
                                size_value.value_multi_option.add(size_option)
                                size_value.save()

                for sku in data['properties']['skus']:
                    if len(sku['properties']) > 1:
                        for att in ch_atrr_op:
                            if sku['properties'][0]['value'] in att:
                                skus_data.append([sku['properties'][0]['value'], att[0]])
                            else:
                                skus_data.append([sku['properties'][1]['value'], att[0]])
                        skus.update({sku['skuId']: skus_data})
                        skus_data = []

                for sku in data["skus"]:
                    if sku['size']:
                        if not ch_atrr_op:
                            product_child = Product.objects.get_or_create(structure='child', parent=product, title=sku['size']['primary'], upc=sku['skuId'])[0]
                            product_child.save()
                            p_ch_att = ProductAttributeValue.objects.get_or_create(product=product_child, attribute=cny_price)[0]
                            p_ch_att.value_integer = sku['cnyPrice']
                            p_ch_att.save()
                            rec = StockRecord.objects.get_or_create(product=product_child, partner=partner, partner_sku=product_child.upc)[0]
                            if sku['cnyPrice'] == 0:
                                print("No price: " + product.title + ", " + product_child.title)
                                rec.price = 0
                                rec.save()
                                continue
                            else:
                                rec.price = int(sku['cnyPrice'] * 15 + 1000)
                                rec.save()
                        else:
                            product_child = Product.objects.get_or_create(structure='child', parent=product, title=sku['size']['primary'], upc=sku['skuId'])[0]
                            product_child.save()
                            p_ch_att = ProductAttributeValue.objects.get_or_create(product=product_child, attribute=cny_price)[0]
                            p_ch_att.value_integer = sku['cnyPrice']
                            p_ch_att.save()
                            for i in range(len(ch_atrr_op)):
                                group = AttributeOptionGroup.objects.get_or_create(name=skus.get(sku['skuId'])[i][1])[0]
                                group.save()
                                ch_att = AttributeOption.objects.get_or_create(option=skus.get(sku['skuId'])[i][0], group=group)[0]
                                ch_att.save()
                                att = ProductAttribute.objects.get_or_create(name=skus.get(sku['skuId'])[i][1], code=translit(skus.get(sku['skuId'])[i][1], "ru", reversed=True), product_class=product_class, type="multi_option", option_group=group)[0]
                                att.save()
                                p_ch_att = ProductAttributeValue.objects.get_or_create(product=product_child, attribute=att)[0]
                                p_ch_att.value_multi_option.add(ch_att)
                                p_ch_att.save()
                            rec = StockRecord.objects.get_or_create(product=product_child, partner=partner, partner_sku=product_child.upc)[0]
                            if sku['cnyPrice'] == 0:
                                logger.info("No price: " + product.title + ", " + product_child.title)
                                rec.price = 0
                                rec.save()
                                continue
                            else:
                                rec.price = int(sku['cnyPrice'] * 15 + 1000)
                                rec.save()
                        try:
                            if skus.get(sku['skuId'])[i][0] == 'Цвет':
                                for image in sku["images"]:
                                    if not ProductImage.objects.filter(caption=image.split('/')[-1]).exists():
                                        img = requests.get(image)
                                        file = open("product_images/product.jpg", 'wb+')
                                        file.write(img.content)
                                        prod_ch_img = ProductImage.objects.get_or_create(product=product_child, original=File(file), caption=image.split('/')[-1])[0]
                                        prod_ch_img.save()
                                        file.close()
                        except TypeError:
                            continue

                for size in data["sizeTable"]:
                    option_group = AttributeOptionGroup.objects.get_or_create(name=size['type'])[0]
                    option_group.save()
                    att = ProductAttribute.objects.get_or_create(name=size['type'], code=size['type'], product_class=product_class, type="multi_option", option_group=option_group)[0]
                    att.save()
                    for values in size['values']:
                        option = AttributeOption.objects.get_or_create(option=values, group=option_group)[0]
                        option.save()
                        p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                        p_att.value_multi_option.add(option)
                        p_att.save()

                for product_property in data["productProperties"]:
                    try:
                        if len(product_property['value']) > 1:
                            option_group = AttributeOptionGroup.objects.get_or_create(name=product_property['translatedKey'])[0]
                            option_group.save()
                            att = ProductAttribute.objects.get_or_create(code=product_property['definitionId'], product_class=product_class, name=product_property['translatedKey'])[0]
                            att.option_group = option_group
                            att.save()
                            att.type = 'multi_option'
                            att.save()
                            for values in product_property['translatedValue']:
                                option = AttributeOption.objects.get_or_create(option=values, group=option_group)[0]
                                option.save()
                                p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                p_att.value_multi_option.add(option)
                                p_att.save()
                        else:
                            att = ProductAttribute.objects.get_or_create(code=product_property['definitionId'], name=product_property['translatedKey'], product_class=product_class)[0]
                            if not att.type == 'multi_option':
                                att.type = 'text'
                                att.save()
                                p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                p_att.value_text = product_property['translatedValue'][0]
                                p_att.save()
                            else:
                                option_group = AttributeOptionGroup.objects.get_or_create(name=product_property['translatedKey'])[0]
                                option_group.save()
                                for values in product_property['translatedValue']:
                                    option = AttributeOption.objects.get_or_create(option=values, group=option_group)[0]
                                    option.save()
                                    p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                    p_att.value_multi_option.add(option)
                                    p_att.save()
                    except:  # noqa: E722
                        if len(product_property['value']) > 1:
                            option_group = AttributeOptionGroup.objects.get_or_create(name=product_property['translatedKey'])[0]
                            option_group.save()
                            att = ProductAttribute.objects.get_or_create(code=translit(product_property['translatedKey'], 'ru', reversed=True), product_class=product_class, name=product_property['translatedKey'])[0]
                            att.option_group = option_group
                            att.type = 'multi_option'
                            att.save()
                            for values in product_property['translatedValue']:
                                option = AttributeOption.objects.get_or_create(option=values, group=option_group)[0]
                                option.save()
                                p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                p_att.value_multi_option.add(option)
                                p_att.save()
                        else:
                            att = ProductAttribute.objects.get_or_create(code=translit(product_property['translatedKey'], 'ru', reversed=True), product_class=product_class, name=product_property['translatedKey'])[0]
                            att.save()
                            if not att.type == 'multi_option':
                                att.type = 'text'
                                p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                p_att.value_text = product_property['translatedValue'][0]
                                p_att.save()
                            else:
                                option_group = AttributeOptionGroup.objects.get_or_create(name=product_property['translatedKey'])[0]
                                option_group.save()
                                for values in product_property['translatedValue']:
                                    option = AttributeOption.objects.get_or_create(option=values, group=option_group)[0]
                                    option.save()
                                    p_att = ProductAttributeValue.objects.get_or_create(product=product, attribute=att)[0]
                                    p_att.value_multi_option.add(option)
                                    p_att.save()
                product.save()
                print("Created succes:" + data['name'], data['article'], product_class)
