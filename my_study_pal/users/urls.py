from django.urls import path
from my_study_pal.users.views import UserInfoViewSet

app_name = "users"

item_list = UserInfoViewSet.as_view({
    'get':'retrieve',
    'post': 'create',
    'put':'update'
})
urlpatterns = [
    path('user_info/', item_list, name='user_info'),
]
