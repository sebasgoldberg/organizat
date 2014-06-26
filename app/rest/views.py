from .serializers import IntervalosMaquinaSerializer
from planificacion.models import MaquinaPlanificacion
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime as DT

class MaquinasYIntervalos(APIView):
    
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, year, month, day, format=None):
        fecha = DT(int(year), int(month), int(day))
        listadoIntervalosMaquinas = []
        for maquina in MaquinaPlanificacion.objects.all():
            intervalos = maquina.get_intervalos_activos_dia(fecha)
            listadoIntervalosMaquinas.append({
                                              'maquina': maquina,
                                              'intervalos': intervalos
                                              })
        serializer = IntervalosMaquinaSerializer(listadoIntervalosMaquinas, many=True)
        return Response(serializer.data)
    