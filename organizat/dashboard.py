# coding=utf-8
"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'iamcast.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name
from django.conf import settings

from datetime import datetime, date, timedelta


class CustomIndexDashboard(Dashboard):

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Produccion'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'produccion.models.Producto',
                      'produccion.models.Maquina',
                      'produccion.models.Tarea',
                      ),
                ),
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'produccion.models.ProductoProxyDependenciasTareas',
                      'produccion.models.TiempoRealizacionTarea',
                      ),
                ),
            ]
        ))

        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Planificacion'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'calendario.models.Calendario',
                      ),
                ),
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'produccion.models.Pedido',
                      ),
                ),
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'planificacion.models.Cronograma',
                      ),
                ),
            ]
        ))

        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Costos'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'costos.models.CostoMaquina',
                      ),
                ),
                modules.ModelList(
                    column=1,
                    collapsible=False,
                    models=(
                      'costos.models.CostoCronograma',
                      ),
                ),
            ]
        ))


        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administracion de usuarios y permisos'),
            column=1,
            collapsible=False,
            models=('django.contrib.*',),
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=True,
            column=2,
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Links'),
            column=3,
            children=[
                {
                    'title': _(u'Visualizar calendario activo'),
                    'url': '/planificacion/calendario/activo/',
                },
            ]
        ))

