from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    fieldsets = (  # добавить подсказки в админку
        (None, {
            'fields': ('name', 'url', 'user', 'state'),
            'description': 'Укажите название магазина, его сайт, привяжите пользователя и установите статус получения заказов.'
        }),
    )
    list_display = ('id', 'name', 'url', 'state', 'user')
    search_fields = ('name', 'url')
    list_filter = ('state',)
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'shops'),
            'description': 'Введите название категории и выберите магазины, к которым она относится.'
        }),
    )
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'category'),
            'description': 'Введите название продукта и выберите его категорию.'
        }),
    )
    list_display = ('id', 'name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('external_id', 'product', 'shop', 'model', 'quantity', 'price', 'price_rrc'),
            'description': (
                'Укажите внешний идентификатор продукта, выберите продукт и магазин, '
                'при необходимости введите модель, количество, цену и рекомендованную розничную цену.'
            )
        }),
    )
    list_display = ('id', 'product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc')
    search_fields = ('product__name',)
    list_filter = ('shop', 'product')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name',),
            'description': 'Введите название параметра, который может использоваться для описания характеристик продуктов.'
        }),
    )
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('product_info', 'parameter', 'value'),
            'description': 'Выберите информацию о продукте, укажите параметр и его значение.'
        }),
    )
    list_display = ('id', 'product_info', 'parameter', 'value')
    search_fields = ('product_info__product__name', 'parameter__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'state', 'contact'),
            'description': 'Создайте заказ, выберите пользователя, укажите статус и свяжите контакт для доставки.'
        }),
        ('Дата заказа', {
            'fields': ('dt',),
            'description': 'Дата и время создания заказа (заполняется автоматически).'
        }),
    )
    readonly_fields = ('dt',)
    list_display = ('id', 'user', 'dt', 'state', 'contact')
    search_fields = ('user__email', 'state')
    list_filter = ('state', 'dt')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('order', 'product_info', 'quantity'),
            'description': 'Выберите заказ, укажите информацию о продукте и его количество.'
        }),
    )
    list_display = ('id', 'order', 'product_info', 'quantity')
    search_fields = ('order__id', 'product_info__product__name')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    class ContactAdmin(admin.ModelAdmin):
        fieldsets = (
            (None, {
                'fields': ('user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone'),
                'description': 'Заполните контактную информацию: город, улицу, дом, дополнительные данные и телефон.'
            }),
        )
        list_display = ('id', 'user', 'city', 'street', 'house', 'phone')
        search_fields = ('user__email', 'city', 'street', 'phone')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'key', 'created_at'),
            'description': 'Токен для подтверждения e-mail.'
        }),
    )
    list_display = ('id', 'user', 'key', 'created_at')
    search_fields = ('user__email',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # количество пустых форм для новых элементов
    verbose_name = 'Элемент заказа'
    verbose_name_plural = 'Элементы заказа'
