from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin

from main_app.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', User_LoginView.as_view(), name='login'),
    url(r'^login/?$', User_LoginView.as_view(), name='login'),
    url(r'^signup/?$', User_SignupView.as_view(), name='signup'),
    url(r'^logout/?$', login_required(User_LogoutView.as_view()), name='logout'),
    url(r'^chat-code/?$', login_required(User_GetCode.as_view()), name='get_code'),
    url(r'^chat/view/?$', login_required(User_ChatView.as_view()), name='view_chat'),
    url(r'^visitor_chat/?$', User_VistorChat.as_view(), name='visitor_chat'),
    url(r'^visitor_requestchat/?$', Vistor_RequestUser.as_view(), name='visitor_requestchat'),
    url(r'^user_message/?$', User_ChatMessage.as_view(), name='user_message'),
    url(r'^visitor_message/?$', Visitor_ChatMessage.as_view(), name='visitor_message'),
    url(r'^chat_history/?$', ChatHistory.as_view(), name='chat_history'),
    url(r'^user_profile/?$', login_required(User_Profile.as_view()), name='user_profile'),
    url(r'^get_visitors/?$', login_required(Get_Visitor.as_view()), name='get_visitors'),
    url(r'^user_delete/?$', login_required(User_FinishChat.as_view()), name='user_delete'),
    url(r'^visitor_delete/?$', login_required(Visitor_FinishChat.as_view()), name='visitor_delete'),
    url(r'^visitor_type/?$', User_Vistor_Typenotification.as_view(), name='visitor_type'),
    url(r'^chat_full_history/?$', login_required(Get_History.as_view()), name='chat_full_history'),
    url(r'^cookie_check/?$', Cookie_Check.as_view(), name='cookie_check'),
    url(r'^admin/', include(admin.site.urls)),
)