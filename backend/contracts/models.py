from django.db import models


class Contract(models.Model):
    contract_id = models.CharField(max_length=80, unique=True)
    modalidad = models.CharField(max_length=120, null=True, blank=True)
    ronda = models.CharField(max_length=20, null=True, blank=True)
    licitacion = models.CharField(max_length=20, null=True, blank=True)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pozos_comprometidos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pozos_terminados = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operador_principal = models.CharField(max_length=255, null=True, blank=True)
    tipo_licitante = models.CharField(max_length=120, null=True, blank=True)
    tipo_yacimiento = models.CharField(max_length=120, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    superficie_km2 = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    fecha_firma = models.DateField(null=True, blank=True)
    duracion_anios = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    vence = models.PositiveIntegerField(null=True, blank=True)
    estatus = models.CharField(max_length=255, null=True, blank=True)
    regla_exploracion = models.TextField(null=True, blank=True)
    no_registro_fiducario = models.CharField(max_length=120, null=True, blank=True)
    fecha_registro_fiducario = models.DateField(null=True, blank=True)
    participacion_estado = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_regalia_adicional = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    incremento_programa_min = models.CharField(max_length=80, null=True, blank=True)
    valor_ponderado_prop_economica = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    resultados = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["contract_id"]

    def __str__(self):
        return self.contract_id


class TimelineEvent(models.Model):
    timeline_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="timeline_events", db_constraint=False)
    fecha = models.DateField(null=True, blank=True)
    evento = models.CharField(max_length=255, null=True, blank=True)
    detalles_evento = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "fecha", "timeline_id"]


class LocationPoint(models.Model):
    point_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="location_points", db_constraint=False)
    numero_vertice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    longitud_decimales = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    latitud_decimales = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "numero_vertice", "point_id"]


class Contractor(models.Model):
    partner_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="contractors", db_constraint=False)
    empresa_nombre = models.CharField(max_length=255, null=True, blank=True)
    tipo_participacion = models.CharField(max_length=120, null=True, blank=True)
    porcentaje_participacion = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    pais_origen = models.CharField(max_length=120, null=True, blank=True)
    actividad_empresarial = models.TextField(null=True, blank=True)
    socios_accionistas_principales = models.TextField(null=True, blank=True)
    cotizacion_bolsa = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "partner_id"]


class Resolution(models.Model):
    resolution_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="resolutions", db_constraint=False)
    actividad_regulada = models.TextField(null=True, blank=True)
    fecha_presentacion = models.DateField(null=True, blank=True)
    fecha_resolucion = models.DateField(null=True, blank=True)
    sentido_resolucion = models.CharField(max_length=120, null=True, blank=True)
    numero_resolucion = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "fecha_resolucion", "resolution_id"]


class PmtSummary(models.Model):
    pmt_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_summaries", db_constraint=False)
    programa_minimo_trabajo_ut = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    incremento_pmt_ut = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    periodo_adicional_ut = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pmt_total_requerido = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    acreditadas_reales = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "pmt_id"]


class PmtWell(models.Model):
    pmt_well_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_wells", db_constraint=False)
    profundidad_metros = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    unidades_trabajo = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    profundidad_perforacion_mbnm = models.CharField(max_length=120, null=True, blank=True)
    tirante_agua_500_1000 = models.CharField(max_length=120, null=True, blank=True)
    tirante_agua_1000_2000 = models.CharField(max_length=120, null=True, blank=True)
    tirante_agua_mayor_2000 = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "pmt_well_id"]


class PmtInfo(models.Model):
    pmt_info_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_info", db_constraint=False)
    actividad_exploratoria = models.CharField(max_length=255, null=True, blank=True)
    descripcion_actividad = models.TextField(null=True, blank=True)
    unidad_medida = models.CharField(max_length=255, null=True, blank=True)
    unidades_trabajo = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "pmt_info_id"]


class PmtStudy(models.Model):
    pmt_study_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_studies", db_constraint=False)
    actividad_exploratoria = models.CharField(max_length=255, null=True, blank=True)
    descripcion_actividad = models.TextField(null=True, blank=True)
    unidad_medida = models.CharField(max_length=255, null=True, blank=True)
    unidades_trabajo = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    estudios_exploratorios = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "pmt_study_id"]


class PmtMethod(models.Model):
    pmt_method_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_methods", db_constraint=False)
    actividad_exploratoria = models.CharField(max_length=255, null=True, blank=True)
    descripcion_actividad = models.TextField(null=True, blank=True)
    unidad_medida = models.CharField(max_length=255, null=True, blank=True)
    unidades_trabajo = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "pmt_method_id"]


class PmtPenalty(models.Model):
    penalty_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="pmt_penalties", db_constraint=False)
    rango_brent_minimo_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rango_brent_maximo_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_por_unidad_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "penalty_id"]


class NationalContentRule(models.Model):
    rule_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="national_content_rules", db_constraint=False)
    etapa = models.CharField(max_length=120, null=True, blank=True)
    porcentaje_base = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    descripcion_regla = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "rule_id"]


class PlanDocument(models.Model):
    document_id = models.CharField(max_length=80, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="plan_documents", db_constraint=False)
    tipo_documento = models.CharField(max_length=255, null=True, blank=True)
    fecha_documento = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "document_id"]


class PlanActivity(models.Model):
    activity_id = models.CharField(max_length=40, primary_key=True)
    document_id = models.CharField(max_length=80, null=True, blank=True)
    sub_actividad = models.CharField(max_length=255, null=True, blank=True)
    tarea_descripcion = models.TextField(null=True, blank=True)
    anio_inicio = models.PositiveIntegerField(null=True, blank=True)
    anio_fin = models.PositiveIntegerField(null=True, blank=True)
    mes_inicio = models.CharField(max_length=40, null=True, blank=True)
    mes_fin = models.CharField(max_length=40, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    ut_aporta = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["document_id", "activity_id"]


class Investment(models.Model):
    investment_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="investments", db_constraint=False)
    anio = models.PositiveIntegerField(null=True, blank=True)
    mes = models.CharField(max_length=40, null=True, blank=True)
    fase_actividad = models.CharField(max_length=120, null=True, blank=True)
    monto_aprobado_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    monto_ejercido_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "anio", "mes", "investment_id"]


class StateRevenue(models.Model):
    revenue_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="state_revenues", db_constraint=False)
    anio = models.PositiveIntegerField(null=True, blank=True)
    mes = models.CharField(max_length=40, null=True, blank=True)
    concepto_pago = models.CharField(max_length=255, null=True, blank=True)
    monto_pagado_mxn = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    monto_pagado_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "anio", "mes", "revenue_id"]


class GeologicalData(models.Model):
    geological_id = models.CharField(max_length=40, primary_key=True)
    contract = models.ForeignKey(Contract, to_field="contract_id", on_delete=models.CASCADE, related_name="geological_data", db_constraint=False)
    provincia_petrolera = models.CharField(max_length=255, null=True, blank=True)
    provincia_geologica = models.CharField(max_length=255, null=True, blank=True)
    superficie_acontractual_km2 = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    cobertura_sismica_3d = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    edad_play = models.CharField(max_length=255, null=True, blank=True)
    litologias = models.TextField(null=True, blank=True)
    hidrocarburo_esperado = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["contract_id", "geological_id"]
