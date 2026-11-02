"""
URL configuration for coursehub_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views  # added for Oct 21 lecture
from django.urls import include, path
from core.auth_views import signup  # added for Oct 26 lecture: public account creation.
from core.search_views import search

urlpatterns = [
    path('admin/', admin.site.urls),
    # add here for Oct 26 lecture
    path("accounts/signup/", signup, name="signup"),
    # add new paths for login/logout here
    path(
        "accounts/login/",  # updated for Oct 26 lecture: match the guide's login URL.
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login"
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(),name="logout"),
    path("api/", include("core.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("search/", search, name="search"),
    path("", include("core.urls"))
]
