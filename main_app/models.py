import uuid, os, pusher, datetime

from django.db import models
from django.contrib.auth.models import User
from urlparse import urlparse
from django.utils.timezone import utc
from django.conf import settings

p = pusher.Pusher(
  app_id='74045',
  key='a8355dbe7a6a0daf08a4',
  secret='5579e9745ca95dcfbaf1'
)

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

def domain_response(request, response):
    referer = urlparse(request.META.get('HTTP_REFERER'))
    try:referer = '{protocol}://{domain}/'.format(protocol=referer[0], domain=referer[1])
    except:pass
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET']
    response['Access-Control-Allow-Origin'] = referer
    response['Access-Control-Allow-Methods'] = ','.join(XS_SHARING_ALLOWED_METHODS)
    return response

def domain_ajax(request, response):
    if request.GET.get('callback'):
        callback = request.GET.get('callback')
        response = callback + '(' + response + ')'
    return response

def get_time_diff(start):
    format_time = '%s-%s-%s %s.%s.%s' %(start.day, start.month, start.year, start.hour, start.minute, start.second)
    return format_time
    
class UserProfile(models.Model):
    user = models.ForeignKey(User)
    user_api = models.CharField(max_length=32, db_index=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    button_name = models.CharField(max_length=32, null=True, blank=True, default="Chat With ME")
    image = models.FileField(upload_to=get_file_path, null=True, blank=True,)

class ChatVisitor(models.Model):
    STATUS_CHOICES = (
        ('W', 'Waiting'),
        ('A', 'Active'),
        ('D', 'Denied'),
        ('F', 'Finished')
    )
    chat_api = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W')  # Waiting status
    url = models.URLField()
    chat_user = models.ForeignKey(UserProfile)
    start_chat = models.DateTimeField(auto_now_add=True)
            
    def new_visitor_chat(self):
        data = {
            'user': self.chat_user.user.username,
            'name': self.name,
            'id': self.id,
            'api': self.chat_api,
            'message': 'You have a new chat request',
        }
        p[self.chat_user.user_api].trigger('visitor_chat', data)
    
    def remove_visitor_chat(self, message=None, notify=None, user=None, user_type=None):
        t = get_time_diff(datetime.datetime.now())
        data = {
            'user': self.chat_user.user.username,
            'name': self.chat_user.user.username,
            'chat': user,
            'time': t,
            'message': message,
            'image': str(self.chat_user.image),
            'user_type': user_type
        }
        p[self.chat_api].trigger(notify, data)
    
class VisitorMessage(models.Model):
    chat_visitor = models.ForeignKey(ChatVisitor)
    message = models.CharField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True)
    chatter = models.CharField(max_length=10, default="visitor")
    
    def visitor_message_chat(self):
        t = get_time_diff(self.datetime)
        data = {
            'user': self.chat_visitor.chat_user.user.username,
            'message': self.message,
            'time': t,
            'chat': 'visitor',
            'name': self.chat_visitor.chat_user.user.username,
            'image': str(self.chat_visitor.chat_user.image),
            'user_type': None
        }
        p[self.chat_visitor.chat_api].trigger('visitor_message', data)
    
    def user_message_chat(self):
        t = get_time_diff(self.datetime)
        data = {
            'user': self.chat_visitor.chat_user.user.username,
            'message': self.message,
            'time': t,
            'chat': 'user',
            'name': self.chat_visitor.name,
            'image': str(self.chat_visitor.chat_user.image),
            'user_type': None
        }
        p[self.chat_visitor.chat_api].trigger('user_message_transfer', data)
        
class VisitorPresence(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    current_url = models.CharField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True)