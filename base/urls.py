from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home,name='home'),
    path("login/", views.user_login,name='user_login'),
    path("logout/", views.user_logout,name='user_logout'),
    path("dashboard/",views.dashboard,name='dashboard'),
    path("view_menu/",views.view_menu,name='view_menu'),
    path("menu_upload/",views.menu_upload,name='menu_upload'),
    path("file_complaint/",views.file_complaint,name='file_complaint'),
    path("view_complaints/",views.view_complaints,name='view_complaints'),
    path("rate_menu/",views.rate_menu,name='rate_menu'),
    path("view_ratings/",views.view_ratings,name='view_ratings'),
    path("calculate_fees/",views.calculate_fees,name='calculate_fees'),
]