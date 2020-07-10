from django.urls import path

from .views import wine_list, wine_detail, new_wine, edit_wine, delete_wine

urlpatterns = [
    path('', wine_list, name='wine_list'),
    path('new', new_wine, name='new_wine'),
    path('<int:wine_id>', wine_detail, name='wine_detail'),
    path('<int:wine_id>/edit', edit_wine, name='edit_wine'),
    path('<int:wine_id>/delete', delete_wine, name='delete_wine'),
]
