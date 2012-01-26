from django.shortcuts import render_to_response
from django.template.context import RequestContext
from cherrypick.main.client import CherrypickClient, Reply
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
import json
from django.forms import Form, fields
from django.views.generic.base import TemplateView, View

def test(request):
    import gevent
    import time
    from random import randint
    
    if 'sleep' in request.GET:
        def stream():
            for i in range(1000):
                #yield 'Jonas...'
                gevent.sleep(0.5)
                yield '%s . ' % randint(0, 1000)
            
        return HttpResponse(stream())
    else:
        return HttpResponse(randint(0, 1000000))
    

class ClientView(View):
    client_timeout = 10000
    client_retries = 1
    
    def __init__(self, *args, **kwargs):
        super(ClientView, self).__init__(*args, **kwargs)
        self.client = CherrypickClient(settings.CLIENT_ENDPOINT, timeout=self.client_timeout, retries=self.client_retries)

class PageView(TemplateView, ClientView):
    def get_template_names(self):
        return ['%s/%s.html' % (__package__.split('.')[-1],
                                self.__class__.__name__[:-4].lower())]

class TodayView(PageView):
    pass
    
class InboxView(PageView):
    def get_context_data(self, inbox):
        return {'inbox': inbox,
                'inboxes': ('sportamore', 'loveyewear', 'propellerheads', 'apica')}

class APIView(ClientView):
    def get(self, request, cmd):
        if request.is_ajax():
            if hasattr(self, cmd):
                reply = getattr(self, cmd)(**request.REQUEST)
            else:
                #from gevent import spawn
                #reply = spawn(self.client.send, cmd).get()
                print cmd, request.REQUEST
                reply = self.client.send(cmd, **request.REQUEST)
            return self.render_to_json(reply)
        
            '''
                API:
                
                create inbox:
                    create project = sportamore
                        create board = inbox
                            create phase = todo
                            create phase = filed
                            
                create task
                
                move task to folder
                
                
                read task
                
            '''
        
        return HttpResponseBadRequest
    
    def post(self, request, cmd):
        return self.get(request, cmd)

    def render_to_json(self, context):
        return HttpResponse(context.serialize(), mimetype='application/json')
    
    def read_task(self, **kwargs):
        return self.client.send('get_task')


def get_client():
    return CherrypickClient(settings.CLIENT_ENDPOINT, timeout=1000, retries=0)

class UpdateItemForm(Form):
    pk = fields.IntegerField()
    index = fields.IntegerField()

def update_item(request):
    if request.is_ajax and request.method == 'POST':
        form = UpdateItemForm(request.POST)
        if form.is_valid():
            pk = form.cleaned_data['pk']
            index = form.cleaned_data['index']
            
            reply = get_client().send('update_item', pk=pk, index=index)
            
            return HttpResponse(reply.serialize(), mimetype='application/json')