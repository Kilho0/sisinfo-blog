from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('django.contrib.auth.urls')),
    path('', include('contas.urls')),
    path('', include('blog.urls')),
]

if not settings.DEBUG:
    # Em produção o Django não serve arquivos estáticos sozinho. Para não
    # depender de pacotes externos, os arquivos coletados pelo collectstatic
    # são servidos pela view embutida do Django, suficiente para este projeto.
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
