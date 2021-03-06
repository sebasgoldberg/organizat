from django.db import models

import django.dispatch

clean_performed = django.dispatch.Signal(providing_args=["instance", ])

class CleanSignal(models.Model):

  def clean(self, *args, **kwargs):
    clean_performed.send(sender=self.__class__, instance=self)

  class Meta:
      abstract = True

