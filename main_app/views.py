import uuid, json
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from main_app.models import *

class User_LoginView(View):
    
    template = "login.html"
    error = ""
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():return redirect('view_chat')
        return render_to_response(self.template, {
                'error':self.error,
                },RequestContext(request))
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('view_chat')
        else:
            self.error = form.errors
        return render_to_response(self.template, {
                'error':self.error,
            },RequestContext(request))

class User_SignupView(View):
    
    template = "login.html"
    message = None
    error = ""
    
    def get(self, request, *args, **kwargs):
        return render_to_response(self.template, {
                'message': self.message,
                'error': self.error
            }, RequestContext(request))
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_all = ['username', 'email', 'password', 'firstname', 'lastname', 'confirm_password']
        for i in list_all:
            if i not in data:self.error = self.error + " " + i
        if self.error == "":
            user = User.objects.create_user(data['username'], data['email'], data["password"])
            user.firstname = data["firstname"]
            user.lastname = data["lastname"]
            user.save()
            userprofile = UserProfile.objects.create(user = user, user_api = uuid.uuid4().hex)
            message = True
        return render_to_response(self.template, {
                'message': self.message,
                'error': self.error
            }, RequestContext(request))
    
class User_ChatView(View):
    
    template = "indexnew.html"
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        chatvisitor = ChatVisitor.objects.filter(chat_user = userprofile, status = "W").order_by('-start_chat')[:5]
        return render_to_response(self.template, {
            'userprofile': userprofile,
            'chatvisitor': chatvisitor,
            'chat_count': len(chatvisitor),
            }, RequestContext(request))
    
    def post(self, request, *args, **kwargs):
        return render_to_response(self.template, {},
                                  RequestContext(request))

class User_VistorChat(View):
    
    response = dict()
    
    def get(self, request, *args, **kwargs):
        uuid_key = request.GET.get('key')
        userprofile = UserProfile.objects.get(user_api = uuid_key)
        url = request.META['HTTP_REFERER']
        visitorpresence = VisitorPresence.objects.create(user_profile = userprofile,
                                                         current_url = url)
        self.response = dict([
            ('user_id', userprofile.id), ('button', userprofile.button_name)
            ])
        response = HttpResponse(domain_ajax(request, json.dumps(self.response)))
        response = domain_response(request, response)
        return response

class Vistor_RequestUser(View):
    
    response = dict()
    
    def get(self, request, *args, **kwargs):
        data = request.GET
        userprofile = UserProfile.objects.get(user_api = data.get('key'))
        chatvisitor = ChatVisitor.objects.create(
            chat_user = userprofile,name= data.get('name'), email = data.get('email'),
            description = data.get('description'), chat_api = uuid.uuid4().hex, url = "http://test.com"
            )
        chatvisitor.new_visitor_chat()
        self.response = dict([
            ('name', chatvisitor.name), ('id', chatvisitor.id), ('date', chatvisitor.start_chat),
            ('user_id', userprofile.id), ('button', userprofile.button_name),
            ('user_name', userprofile.user.username), ('api_key', chatvisitor.chat_api)
            ])
        response = HttpResponse(domain_ajax(request, json.dumps(self.response, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response

class Visitor_ChatMessage(View):
    
    response = dict()
    
    def get(self, request, *args, **kwargs):
        data = request.GET
        chatvisitor = ChatVisitor.objects.get(id = data.get('id'))
        visitormessage = VisitorMessage.objects.create(chat_visitor = chatvisitor,
                                                       message = data.get('message'), chatter="visitor")
        visitormessage.user_message_chat()
        self.response = dict([
            ('name', chatvisitor.name), ('message', visitormessage.message),
            ('time', get_time_diff(visitormessage.datetime)), ('chat', 'user'),
            ('image', str(chatvisitor.chat_user.image))
            ])
        response = HttpResponse(domain_ajax(request, json.dumps(self.response, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response

class User_ChatMessage(View):
    
    response = dict()
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        chatvisitor = ChatVisitor.objects.get(id = data['chat_id'])
        visitormessage = VisitorMessage.objects.create(chat_visitor = chatvisitor,
                                                       message = data['message'], chatter="user")
        visitormessage.visitor_message_chat()
        self.response = dict([
            ('name', request.user.username), ('message', visitormessage.message),
            ('time', get_time_diff(visitormessage.datetime)), ('chat', 'user'),
            ('image', str(chatvisitor.chat_user.image))
            ])
        response = HttpResponse(domain_ajax(request, json.dumps(self.response, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(User_ChatMessage, self).dispatch(*args, **kwargs)

class ChatHistory(View):
    
    def get(self, request, *args, **kwargs):
        response_list = []
        userprofile = UserProfile.objects.get(user = request.user)
        chatvisitor = ChatVisitor.objects.get(id = request.GET['chat_id'])
        visitormessage = VisitorMessage.objects.filter(chat_visitor = chatvisitor).order_by('datetime')
        if visitormessage:
            for i in visitormessage:
                response_list.append({'message': i.message, 'id': i.id,
                                       'time': i.datetime, 'chatter': i.chatter,
                                       'username': request.user.username,
                                       'name': i.chat_visitor.name,
                                       'image': str(i.chat_visitor.chat_user.image)
                                        })
        response= [{'response':response_list}, {'chatapi': str(chatvisitor.chat_api)}]
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type='application/json')
    
class User_GetCode(View):
    
    template = "get-code.html"
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        return render_to_response(self.template, {
                'userprofile': userprofile,
                'request_url': request.META['HTTP_HOST']
            }, RequestContext(request))

class User_Profile(View):
    
    template = "userprofile.html"
    message = None
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        return render_to_response(self.template, {
                'message': self.message,
                'userprofile': userprofile,
                'user': request.user
            }, RequestContext(request))
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        user = request.user
        userprofile = UserProfile.objects.get(user = user)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.save()
        userprofile.phone = int(data['phone'])
        userprofile.button_name = data['button_name']
        if request.FILES.has_key('file'):
            userprofile.image = request.FILES['file']
        userprofile.save()
        return render_to_response(self.template, {
                'message': "Profile has been successfully updated",
                'userprofile': userprofile,
                'user': request.user
            }, RequestContext(request))
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(User_Profile, self).dispatch(*args, **kwargs)

class Get_Visitor(View):
    
    template = "getvisitors.html"
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        visitorpresence = VisitorPresence.objects.filter(user_profile = userprofile)
        paginator = Paginator(visitorpresence, 10)
        if request.GET.has_key('page'):page = request.GET['page']
        else:page = 1
        if request.is_ajax():
            query = request.GET.get('page')
            if query is not None:page = query
        try:visitorpresence = paginator.page(page)
        except (EmptyPage, InvalidPage):visitorpresence = paginator.page(paginator.num_pages)
        return render_to_response(self.template, {
            'userprofile':userprofile,
            'visitorpresence':visitorpresence
            }, RequestContext(request))
    
class Get_History(View):
    
    template = "chathistory.html"
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        chatvisitor = ChatVisitor.objects.filter(chat_user = userprofile)
        paginator = Paginator(chatvisitor, 10)
        if request.GET.has_key('page'):page = request.GET['page']
        else:page = 1
        if request.is_ajax():
            query = request.GET.get('page')
            if query is not None:page = query
        try:chatvisitor = paginator.page(page)
        except (EmptyPage, InvalidPage):chatvisitor = paginator.page(paginator.num_pages)
        return render_to_response(self.template,
                                    {
                                    'userprofile':userprofile,
                                    'chatvisitor':chatvisitor
                                    }, RequestContext(request))
    
class User_FinishChat(View):
    
    def get(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user = request.user)
        chatvisitor = ChatVisitor.objects.get(id = request.GET['chat_id'])
        chatvisitor.status = "F"
        chatvisitor.save()
        chatvisitor.remove_visitor_chat(message = 'The chat has been closed by user',
                                        notify = "visitor_message", user="visitor")
        return HttpResponse(str(chatvisitor.id))

class User_Vistor_Typenotification(View):
    
    def get(self, request, *args, **kwargs):
        chatvisitor = ChatVisitor.objects.get(id = request.GET['chat_id'])
        user = request.GET['type']
        if request.GET['chat'] == "visitor":
            chatvisitor.remove_visitor_chat(message = chatvisitor.name,
                                        notify = "user_message_transfer", user=user, user_type="type")
        else:
            chatvisitor.remove_visitor_chat(message = chatvisitor.chat_user.user.username,
                                        notify = "visitor_message", user=user, user_type="type")
        self.response={'success': True}
        response = HttpResponse(domain_ajax(request, json.dumps(self.response, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response


class Visitor_FinishChat(View):
    
    def get(self, request, *args, **kwargs):
        chatvisitor = ChatVisitor.objects.get(id = request.GET['chat_id'])
        chatvisitor.status = "F"
        chatvisitor.save()
        chatvisitor.remove_visitor_chat(message = 'The chat has been closed by Visitor',
                                        notify = "user_message_transfer", user="user")
        response = HttpResponse(domain_ajax(request, json.dumps({'success':True}, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response

class Cookie_Check(View):
    
    def get(self, request, *args, **kwargs):
        response = {'success': 'occupy'}
        response_list = []
        chatvisitor = ChatVisitor.objects.get(chat_api = request.GET['cookie'])
        visitormessage = VisitorMessage.objects.filter(chat_visitor = chatvisitor).order_by('datetime')
        dict_update = {'user_name':chatvisitor.chat_user.user.username,
                       'id':chatvisitor.id,'api_key':chatvisitor.chat_api,
                       'user_id': chatvisitor.chat_user.id, 'button': chatvisitor.chat_user.button_name}
        if visitormessage:
            for i in visitormessage:
                if i.chatter == "visitor":name = i.chat_visitor.name
                else:name = chatvisitor.chat_user.user.username
                add = {'message': i.message, 'id': i.id,
                        'time': i.datetime, 'chat': i.chatter,
                        'name': name,
                        'image': str(i.chat_visitor.chat_user.image),
                        'user_type' : "chat"
                         }
                response_list.append(add)
        response= [{'response':response_list}, {'chatapi': dict_update}]
        response = HttpResponse(domain_ajax(request, json.dumps(response, cls=DjangoJSONEncoder)))
        response = domain_response(request, response)
        return response


class User_LogoutView(View):
    
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect('login')