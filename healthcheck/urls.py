from django.contrib import admin
from django.conf import settings
from django.urls import path, include  # noqa: F401
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('api/', include('api.urls', namespace='api')), # TODO
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
