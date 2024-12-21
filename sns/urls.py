# 2024/12/21 update
from django.urls import path
from . import views
from .views import health_check
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import chat
from .views import chat_page
# app_name='sns'

urlpatterns = [
    path('', views.top, name='top'),
    path('index', views.index, name='index'),
    path('index/<int:page>/', views.index, name='index'),
    path('delete/<int:num>', views.delete, name='delete'),
    path('edit/<int:num>', views.edit, name='edit'),
    path('comment', views.comment, name='comment'),
    path('groups', views.groups, name='groups'),
    path('add', views.add, name='add'),
    path('join', views.join, name='join'),
    path('rjct', views.rjct, name='rjct'),
    path('creategroup', views.creategroup, name='creategroup'),
    path('post', views.post, name='post'),
    path('share/<int:share_id>', views.share, name='share'),
    path('good/<int:good_id>', views.good, name='good'),
    path('health_check/', health_check, name='health_check'),    # urlsに追加

    path('upload_video', views.upload_video, name='upload_video'),
    path('video_list', views.video_list, name='video_list'),

    path('display_video/<int:video_id>/', views.display_video, name='display_video'),
    path('chat/', chat, name='chat'),
    path('chat_page', chat_page, name='chat_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
