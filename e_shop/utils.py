from django.db.models import Count

from .models import Category

menu = [{'title': "Add Category ", 'url_name': 'add-category'},
        {'title': "Add Product ", 'url_name': 'add-product'},
        {'title': "Show Refunds ", 'url_name': 'admin-refund'},
        ]


class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        categories = Category.objects.annotate(Count('product'))
        context['categories'] = categories

        if self.request.user.is_superuser:
            context['menu'] = menu

        if 'cat_selected' not in context:
            context['cat_selected'] = 0

        return context
