from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, LineaTiempo, Ubicacion, Contratista, PmtResumen, InversionEjercida, DatoGeologico

class DashboardDataView(APIView):
    # permission_classes = [IsAuthenticated] # Optional: Protect it if needed.

    def get(self, request):
        contratos = Contrato.objects.all()
        inversiones = InversionEjercida.objects.all()
        pmts = PmtResumen.objects.all()
        ubicaciones = Ubicacion.objects.all()
        lineas = LineaTiempo.objects.all()
        contratistas = Contratista.objects.all()
        geologicos = DatoGeologico.objects.all()

        payload = {
            "contratoIds": [c.contrato_id for c in contratos],
            "contratos": [
                {
                    "contratoId": c.contrato_id,
                    "operadorPrincipal": c.operador_principal,
                    "modalidad": c.modalidad,
                    "fechaFirma": c.fecha_firma,
                    "vence": c.vence,
                    "tipoYacimient": c.tipo_yacimiento,
                    "participacionEstado": float(c.participacion_estado) if c.participacion_estado else 0,
                    "pozosComprometidos": c.pozos_comprometidos,
                    "pozosTerminados": c.pozos_terminados,
                    "estatus": c.estatus,
                    "estado": c.estado,
                    "superficie": c.superficie_km2,
                }
                for c in contratos
            ],
            "inversiones": [
                {
                    "contratoId": i.contrato_id,
                    "anio": i.anio,
                    "mes": i.mes,
                    "montoEjercidoUsd": float(i.monto_ejercido_usd) if i.monto_ejercido_usd else 0
                }
                for i in inversiones
            ],
            "programasMinimosTrabajo": [
                {
                    "contratoId": p.contrato_id,
                    "programaMinimoTrabajoUt": float(p.programa_minimo) if p.programa_minimo else 0,
                    "incrementoPmtUt": float(p.incremento) if p.incremento else 0,
                    "periodoAdicionalUt": float(p.periodo_adicional) if p.periodo_adicional else 0,
                    "pmtTotalRequerido": float(p.total_requerido) if p.total_requerido else 0,
                    "acreditadasReales": float(p.acreditadas) if p.acreditadas else 0,
                    "fechaLimite": p.fecha_limite
                }
                for p in pmts
            ],
            "ubicaciones": [
                {
                    "contratoId": u.contrato_id,
                    "numeroVertice": u.numero_vertice,
                    "longitudDecimales": float(u.longitud) if u.longitud else 0,
                    "latitudDecimales": float(u.latitud) if u.latitud else 0
                }
                for u in ubicaciones
            ],
            "lineasTiempo": [
                {
                    "contratoId": l.contrato_id,
                    "fecha": l.fecha,
                    "evento": l.evento,
                    "detallesEvento": l.detalles
                }
                for l in lineas
            ],
            "contratistas": [
                {
                    "contratoId": c.contrato_id,
                    "empresaNombre": c.empresa_nombre,
                    "tipoParticipacion": c.tipo_participacion,
                    "porcentajeParticipacion": float(c.porcentaje_participacion) if c.porcentaje_participacion else None
                }
                for c in contratistas
            ],
            "geologicos": [
                {
                    "geologicoId": g.id_datgeo,
                    "contratoId": g.contrato_id,
                    "ProvinciaPetrolera": g.provincia_petrolera,
                    "ProvinciaGeologica": g.provincia_geologica,
                    "SuperficieAcontractual": g.superficie,
                    "CoberturaSismica3D": g.cobertura,
                    "EdadPlay": g.edad_play,
                    "Litologia": g.litologias,
                    "HidrocarburoEsperado": g.hidrocarburo
                }
                for g in geologicos
            ]
        }

        return Response(payload)

class ContratoListView(APIView):
    def get(self, request):
        contratos = Contrato.objects.all()
        data = [
            {
                "id": c.contrato_id,
                "contract_id": c.contrato_id,
                "operador_principal": c.operador_principal,
                "modalidad": c.modalidad,
                "tipo_yacimiento": c.tipo_yacimiento,
                "estado": c.estado,
                "estatus": c.estatus,
                "area": c.area,
                "superficie_km2": c.superficie_km2
            }
            for c in contratos
        ]
        return Response(data)

from django.shortcuts import get_object_or_404

class ContratoDetailView(APIView):
    def get(self, request, pk):
        c = get_object_or_404(Contrato, contrato_id=pk)
        data = {
            "id": c.contrato_id,
            "contract_id": c.contrato_id,
            "modalidad": c.modalidad,
            "ronda": c.ronda,
            "licitacion": c.licitacion,
            "area": c.area,
            "pozos_comprometidos": c.pozos_comprometidos,
            "pozos_terminados": c.pozos_terminados,
            "operador_principal": c.operador_principal,
            "tipo_licitante": c.tipo_licitante,
            "tipo_yacimiento": c.tipo_yacimiento,
            "estado": c.estado,
            "superficie_km2": c.superficie_km2,
            "fecha_firma": c.fecha_firma,
            "duracion_anios": c.duracion_anios,
            "vence": c.vence,
            "estatus": c.estatus,
            "participacion_estado": c.participacion_estado
        }
        return Response(data)

    def put(self, request, pk):
        c = get_object_or_404(Contrato, contrato_id=pk)
        data = request.data
        c.modalidad = data.get('modalidad', c.modalidad)
        c.ronda = data.get('ronda', c.ronda)
        c.licitacion = data.get('licitacion', c.licitacion)
        c.area = data.get('area', c.area)
        c.pozos_comprometidos = data.get('pozos_comprometidos', c.pozos_comprometidos) or None
        c.pozos_terminados = data.get('pozos_terminados', c.pozos_terminados) or None
        c.operador_principal = data.get('operador_principal', c.operador_principal)
        c.tipo_licitante = data.get('tipo_licitante', c.tipo_licitante)
        c.tipo_yacimiento = data.get('tipo_yacimiento', c.tipo_yacimiento)
        c.estado = data.get('estado', c.estado)
        c.superficie_km2 = data.get('superficie_km2', c.superficie_km2) or None
        c.fecha_firma = data.get('fecha_firma', c.fecha_firma)
        c.duracion_anios = data.get('duracion_anios', c.duracion_anios) or None
        c.vence = data.get('vence', c.vence)
        c.estatus = data.get('estatus', c.estatus)
        c.participacion_estado = data.get('participacion_estado', c.participacion_estado) or None
        c.save()
        return Response({"status": "success"})

from rest_framework import viewsets
from .serializers import (
    LineaTiempoSerializer, UbicacionSerializer, ContratistaSerializer,
    PmtResumenSerializer, InversionEjercidaSerializer, DatoGeologicoSerializer
)

class LineaTiempoViewSet(viewsets.ModelViewSet):
    serializer_class = LineaTiempoSerializer
    def get_queryset(self):
        qs = LineaTiempo.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs

class UbicacionViewSet(viewsets.ModelViewSet):
    serializer_class = UbicacionSerializer
    def get_queryset(self):
        qs = Ubicacion.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs

class ContratistaViewSet(viewsets.ModelViewSet):
    serializer_class = ContratistaSerializer
    def get_queryset(self):
        qs = Contratista.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs

class PmtResumenViewSet(viewsets.ModelViewSet):
    serializer_class = PmtResumenSerializer
    def get_queryset(self):
        qs = PmtResumen.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs

class InversionEjercidaViewSet(viewsets.ModelViewSet):
    serializer_class = InversionEjercidaSerializer
    def get_queryset(self):
        qs = InversionEjercida.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs

class DatoGeologicoViewSet(viewsets.ModelViewSet):
    serializer_class = DatoGeologicoSerializer
    def get_queryset(self):
        qs = DatoGeologico.objects.all()
        cid = self.request.query_params.get('contrato_id')
        if cid: qs = qs.filter(contrato_id=cid)
        return qs
