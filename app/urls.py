from django.urls import path
from app.views import *
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('login/', obtain_jwt_token),
    path('user', UserAPIView.as_view()),
    path('queue', QueueAPIView.as_view()),
    path('queue/<int:code>/members', queue),
    path('queue/<int:code>/info', queue_info),
    path('queue/<int:code>/removeme', queue_remove),
]
