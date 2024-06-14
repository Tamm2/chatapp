from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('friends', views.friends, name='friends'),
    path('talk_room/<int:user_id>', views.talk_room, name='talk_room'),
    path('setting', views.setting, name='setting'),
    path('username_change',views.username_change,name="username_change"),
    path('email_change',views.email_change,name="email_change"),
    path('image_change',views.image_change,name='image_change'),
    path('password_change',views.PasswordChange.as_view(),name='password_change'),
    path("change_done",views.change_done,name="change_done"),
    path("logout/", views.logout_view, name="logout"),
    path('inquiry',views.inquiry,name='inquiry'),
    path('inquiry_confirm',views.inquiry_confirm,name="inquiry_confirm"),
    path('inquiry/success/', views.inquiry_success, name='inquiry_success'),
]
