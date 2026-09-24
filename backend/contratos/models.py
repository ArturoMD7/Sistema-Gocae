from django.db import models

class Contrato(models.Model):
    contrato_id = models.CharField(max_length=100, primary_key=True)
    modalidad = models.CharField(max_length=255, null=True, blank=True)
    ronda = models.CharField(max_length=100, null=True, blank=True)
    licitacion = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    pozos_comprometidos = models.IntegerField(null=True, blank=True)
    pozos_terminados = models.IntegerField(null=True, blank=True)
    operador_principal = models.CharField(max_length=255, null=True, blank=True)
    tipo_licitante = models.CharField(max_length=100, null=True, blank=True)
    tipo_yacimiento = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=100, null=True, blank=True)
    superficie_km2 = models.FloatField(null=True, blank=True)
    fecha_firma = models.CharField(max_length=50, null=True, blank=True)
    duracion_anios = models.FloatField(null=True, blank=True)
    vence = models.CharField(max_length=50, null=True, blank=True)
    estatus = models.CharField(max_length=100, null=True, blank=True)
    participacion_estado = models.FloatField(null=True, blank=True)

class LineaTiempo(models.Model):
    id_timeline = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='lineas_tiempo')
    fecha = models.CharField(max_length=100, null=True, blank=True)
    evento = models.TextField(null=True, blank=True)
    detalles = models.TextField(null=True, blank=True)

class Ubicacion(models.Model):
    id_punto = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='ubicaciones')
    numero_vertice = models.IntegerField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)

class Contratista(models.Model):
    id_socio = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='contratistas')
    empresa_nombre = models.CharField(max_length=255, null=True, blank=True)
    tipo_participacion = models.CharField(max_length=100, null=True, blank=True)
    porcentaje_participacion = models.FloatField(null=True, blank=True)

class PmtResumen(models.Model):
    id_pmt = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='pmt')
    programa_minimo = models.FloatField(null=True, blank=True)
    incremento = models.FloatField(null=True, blank=True)
    periodo_adicional = models.FloatField(null=True, blank=True)
    total_requerido = models.FloatField(null=True, blank=True)
    acreditadas = models.FloatField(null=True, blank=True)
    fecha_limite = models.CharField(max_length=50, null=True, blank=True)

class InversionEjercida(models.Model):
    id_inversion = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='inversiones')
    anio = models.IntegerField(null=True, blank=True)
    mes = models.CharField(max_length=50, null=True, blank=True)
    monto_ejercido_usd = models.FloatField(null=True, blank=True)

class DatoGeologico(models.Model):
    id_datgeo = models.CharField(max_length=50, primary_key=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='geologicos')
    provincia_petrolera = models.CharField(max_length=255, null=True, blank=True)
    provincia_geologica = models.CharField(max_length=255, null=True, blank=True)
    superficie = models.CharField(max_length=255, null=True, blank=True)
    cobertura = models.CharField(max_length=255, null=True, blank=True)
    edad_play = models.CharField(max_length=255, null=True, blank=True)
    litologias = models.TextField(null=True, blank=True)
    hidrocarburo = models.CharField(max_length=255, null=True, blank=True)
