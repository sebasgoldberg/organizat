from django.shortcuts import render
from django.views.generic.base import TemplateView

class AppView(TemplateView):

  def get(self, request, *args, **kwargs):
    path = self.kwargs['path']
    if path == '':
      path = 'index.html'
    self.template_name = 'app/%s' % path
    return super(AppView, self).get(request, *args, **kwargs)
