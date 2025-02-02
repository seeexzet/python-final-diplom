from django import forms
from dal import autocomplete
from .models import Order

class OrderAdminForm(forms.ModelForm):  # форма нужна для автоподгрузки адресов конкретного пользователя при его выборе
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            # 'contact' будет автодополняться, значение user будет передаваться в AJAX-запрос.
            'contact': autocomplete.ModelSelect2(
                url='backend:contact-autocomplete',
                forward=['user']
            ),
        }
