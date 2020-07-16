from django.contrib import admin
from django.urls import path, include  # noqa: F401

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('api/', include('api.urls', namespace='api')), # TODO
]
