from rest_framework import serializers

from planificacion.models import MaquinaPlanificacion, IntervaloCronograma

class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaquinaPlanificacion

class IntervaloSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervaloCronograma
        fields = ('id', 'fecha_desde', 'fecha_hasta',)

class IntervalosMaquinaSerializer(serializers.Serializer):
    
    maquina = MaquinaSerializer()
    intervalos = IntervaloSerializer(many=True)