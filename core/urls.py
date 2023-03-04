from django.contrib import admin
from django.urls import path, include

# from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,
#     TokenBlacklistView)

import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('LittleLemonAPI.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.authtoken')),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("__debug__", include(debug_toolbar.urls)),
]
