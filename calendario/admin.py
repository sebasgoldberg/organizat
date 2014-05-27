from django.contrib import admin
from .models import Calendario, IntervaloLaborable, ExcepcionLaborable

class IntervaloLaborableInline(admin.TabularInline):
  model=IntervaloLaborable
  extra = 1

class ExcepcionLaborableInline(admin.TabularInline):
  model=ExcepcionLaborable
  extra = 1

class CalendarioAdmin(admin.ModelAdmin):
  inlines=[IntervaloLaborableInline,ExcepcionLaborableInline]

admin.site.register(Calendario,CalendarioAdmin)
