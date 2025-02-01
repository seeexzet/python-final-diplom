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
    list_display = ('id', 'name', 'url', 'state', 'user')
    search_fields = ('name', 'url')
    list_filter = ('state',)
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc')
    search_fields = ('product__name',)
    list_filter = ('shop', 'product')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductInfoAdmin(admin.ModelAdmin):
    pass

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'state', 'contact')
    search_fields = ('user__email', 'state')
    list_filter = ('state', 'dt')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'street', 'house', 'phone')
    search_fields = ('user__email', 'city', 'street', 'phone')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'key', 'created_at')
    search_fields = ('user__email',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # сколько пустых форм добавить для новых элементов

