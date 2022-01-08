from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('loginpage/', views.login_page, name='login_page'),
    path('login/', views.handleLogin, name='login'),
    path('signupuser/', views.handleSignUpUser, name='signupuser'),
    path('signupfarmer/', views.handleSignUpFarmer, name='signupfarmer'),
    path('logout/', views.handleLogout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('shop/', views.shop, name='shop'),
    path('request/', views.requestGoods, name='requestGoods'),
    path('allocations/', views.allocatedGoods, name='allocatedGoods'),
    path('addgoods/', views.addGoods, name="addGoods"),
    path('placerequestgoods/', views.placeRequestGoods, name="placeRequestGoods"),
    path('adminhome/', views.adminHome, name="adminHome"),
    path('distribute/', views.distribute, name="distribute"),
    path('donatedgoods/', views.donatedGoods, name="donatedGoods"),
    path('donatedcoins/', views.donatedCoins, name="donatedCoins"),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)