from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from recibos.views import (
    home,
    recibo_list,
    recibo_detail,
    recibo_create,
    recibo_update,
    recibo_delete,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('recibos/', recibo_list, name='recibo_list'),
    path('recibos/nuevo/', recibo_create, name='recibo_create'),
    path('recibos/<int:pk>/', recibo_detail, name='recibo_detail'),
    path('recibos/<int:pk>/editar/', recibo_update, name='recibo_update'),
    path('recibos/<int:pk>/eliminar/', recibo_delete, name='recibo_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
