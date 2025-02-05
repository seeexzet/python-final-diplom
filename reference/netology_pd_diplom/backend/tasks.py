import json
import logging
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.db import IntegrityError

logger = logging.getLogger(__name__)

FILE_PATH = getattr(settings, 'IMPORT_FILE_PATH', 'importfile.json')


@shared_task
def send_email(to_email, subject, message):
    """
    Задача для отправки email. Используются настройки SMTP из settings.py.
    """
    print('Отправка email...')
    try:
        result = django_send_mail(
            subject=subject,
            message=message,
            from_email=settings.SERVER_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return f"Email отправлено успешно. Результат: {result}"
    except Exception as e:
        logger.error("Ошибка при отправке email: %s", e)
        return f"Ошибка при отправке email: {e}"


def convert_foreign_keys(model, record):
    """
    Для каждого поля, которое является внешним ключом, если значение в записи является int,
    пытаемся получить соответствующий экземпляр модели.
    """
    for field_name, value in record.items():
        try:
            field = model._meta.get_field(field_name)
        except Exception:
            continue

        if field.is_relation and value is not None and isinstance(value, int):
            remote_model = field.remote_field.model
            try:
                record[field_name] = remote_model.objects.get(pk=value)
            except remote_model.DoesNotExist:
                # Если объекта нет, не меняем значение, чтобы при сохранении возникла ошибка.
                pass
    return record


@shared_task
def do_import():
    """
    Задача импорта данных из JSON-файла. Файл берётся из пути, заданного в настройках (IMPORT_FILE_PATH).
    User: если пользователь с таким же email уже существует, запись пропускается.
    Shop: если магазин с указанным пользователем уже существует, запись пропускается.
    ProductInfo: если запись с данным external_id уже существует для указанного магазина и продукта, запись пропускается.
    OrderItem: если запись с указанными order и product_info уже существует, запись пропускается.
    ProductParameter: если запись с теми же product_info и parameter уже существует, запись пропускается.
    ConfirmEmailToken: если запись с тем же key уже существует, запись пропускается.
    При отсутствии категории или магазина запись не создаётся.
    Удаляется поле id и преобразуются внешние ключи.
    """
    errors = []
    FILE_PATH = getattr(settings, 'IMPORT_FILE_PATH', 'importfile.json')

    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        error_msg = f"Ошибка чтения файла {FILE_PATH}: {e}"
        logger.error(error_msg)
        send_email.delay(settings.SERVER_EMAIL, "Import Error", error_msg)
        return error_msg

    for model_name, records in data.items():
        try:
            model = apps.get_model('backend', model_name)
        except Exception as e:
            error_msg = f"Модель '{model_name}' не найдена: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

        for rec in records:
            try:
                # Удаляем ключ "id", чтобы не возникало конфликтов с первичным ключом
                rec.pop("id", None)

                # Для модели User: проверяем по email
                if model_name == "User":
                    email = rec.get("email")
                    if email and model.objects.filter(email=email).exists():
                        logger.info(f"Пользователь с email {email} уже существует. Не заносим в базу.")
                        continue

                # Для модели Shop: проверяем по внешнему ключу user
                if model_name == "Shop":
                    # Пока rec['user'] еще целое число, поэтому сначала конвертируем внешние ключи
                    rec = convert_foreign_keys(model, rec)
                    user_obj = rec.get("user")
                    if user_obj and model.objects.filter(user_id=user_obj.pk).exists():
                        logger.info(f"Магазин для пользователя {user_obj.pk} уже существует. Не заносим в базу.")
                        continue

                # Для модели ProductInfo: проверяем уникальность по external_id, shop и product
                if model_name == "ProductInfo":
                    external_id = rec.get("external_id")
                    shop_id = rec.get("shop")
                    product_id = rec.get("product")
                    if external_id and shop_id and product_id:
                        if model.objects.filter(external_id=external_id,
                                                shop_id=shop_id,
                                                product_id=product_id).exists():
                            logger.info(
                                f"Запись ProductInfo с external_id {external_id}, shop {shop_id} и product {product_id} уже существует. Не заносим в базу."
                            )
                            continue

                # Преобразуем внешние ключи (если еще не сделали этого для модели Shop)
                rec = convert_foreign_keys(model, rec)

                # Для модели OrderItem: проверяем уникальность по order и product_info
                if model_name == "OrderItem":
                    order_obj = rec.get("order")
                    product_info_obj = rec.get("product_info")
                    if order_obj and product_info_obj:
                        if model.objects.filter(order_id=order_obj.pk, product_info_id=product_info_obj.pk).exists():
                            logger.info(
                                f"Запись OrderItem с order_id {order_obj.pk} и product_info_id {product_info_obj.pk} уже существует. Не заносим в базу."
                            )
                            continue

                # Для модели ProductParameter: проверяем уникальность по product_info и parameter
                if model_name == "ProductParameter":
                    product_info_obj = rec.get("product_info")
                    parameter_obj = rec.get("parameter")
                    if product_info_obj and parameter_obj:
                        if model.objects.filter(product_info_id=product_info_obj.pk,
                                                parameter_id=parameter_obj.pk).exists():
                            logger.info(
                                f"Запись ProductParameter с product_info_id {product_info_obj.pk} и parameter_id {parameter_obj.pk} уже существует. Пропускаем."
                            )
                            continue

                # Для модели ConfirmEmailToken: проверяем уникальность по key
                if model_name == "ConfirmEmailToken":
                    token_key = rec.get("key")
                    if token_key and model.objects.filter(key=token_key).exists():
                        logger.info(
                            f"Запись ConfirmEmailToken с key {token_key} уже существует. Пропускаем."
                        )
                        continue

                # Попытка записать в базу
                instance = model(**rec)
                try:
                    instance.save()
                except IntegrityError as e:
                    # Если возникает ошибка уникального ограничения, пропускаем запись
                    if model_name in ["OrderItem", "ProductParameter", "ConfirmEmailToken"]:
                        logger.info(
                            f"Запись для модели '{model_name}' с данными {rec} уже существует (IntegrityError). Не заносим в базу."
                        )
                        continue
                    else:
                        raise e

            except Exception as e:
                error_msg = f"Ошибка импорта записи для модели '{model_name}': {rec}. Ошибка: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

    if errors:
        summary = "\n".join(errors)
        send_email.delay(settings.SERVER_EMAIL, "Import Errors Occurred", summary)
        result_msg = f"Импорт завершён с ошибками:\n{summary}"
    else:
        result_msg = "Импорт завершён успешно без ошибок."

    logger.info(result_msg)
    return result_msg