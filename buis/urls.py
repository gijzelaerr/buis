from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scheduler/', include('scheduler.urls')),
    path('frontend/', include('frontend.urls')),
]
