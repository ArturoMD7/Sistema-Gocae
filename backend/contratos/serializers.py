from rest_framework import serializers
from .models import LineaTiempo, Ubicacion, Contratista, PmtResumen, InversionEjercida, DatoGeologico

class LineaTiempoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaTiempo
        fields = '__all__'

class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = '__all__'

class ContratistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contratista
        fields = '__all__'

class PmtResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmtResumen
        fields = '__all__'

class InversionEjercidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InversionEjercida
        fields = '__all__'

class DatoGeologicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatoGeologico
        fields = '__all__'
