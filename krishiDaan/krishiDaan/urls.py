from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.loginpage, name='loginpage'),
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
    # path('postsign/', views.postsign, name='postsign'),
    # path('logout/', views.logout, name='logout'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)