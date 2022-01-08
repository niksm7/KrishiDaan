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
    path('donations/', views.donations, name='donations'),
    path('request/', views.requestGoods, name='requestGoods'),
    path('pending/', views.pendingRequest, name='pendingRequest'),
    path('allocations/', views.allocatedGoods, name='allocatedGoods'),
    # path('postsign/', views.postsign, name='postsign'),
    # path('logout/', views.logout, name='logout'),
    

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)