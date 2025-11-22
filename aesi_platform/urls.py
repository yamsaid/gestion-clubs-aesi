"""
URL configuration for aesi_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('users.urls')),
    
    # Apps
    path('', include('core.urls')),
    path('clubs/', include('clubs.urls')),
    path('participation/', include('participation.urls')),
    path('finances/', include('finances.urls')),
    path('dashboard/', include('dashboard.urls')),
    
    # API
    path('api/', include('clubs.api_urls')),
    path('api/participation/', include('participation.api_urls')),
    path('api/finances/', include('finances.api_urls')),
    path('api/dashboard/', include('dashboard.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin
admin.site.site_header = "AESI Platform Administration"
admin.site.site_title = "AESI Platform Admin"
admin.site.index_title = "Bienvenue sur la plateforme de gestion AESI"
