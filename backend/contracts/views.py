from django.db.models import Count, Sum
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Contract,
    Contractor,
    GeologicalData,
    Investment,
    LocationPoint,
    NationalContentRule,
    PlanActivity,
    PlanDocument,
    PmtInfo,
    PmtMethod,
    PmtPenalty,
    PmtStudy,
    PmtSummary,
    PmtWell,
    Resolution,
    StateRevenue,
    TimelineEvent,
)
from .serializers import (
    ContractSerializer,
    ContractorSerializer,
    GeologicalDataSerializer,
    InvestmentSerializer,
    LocationPointSerializer,
    NationalContentRuleSerializer,
    PlanActivitySerializer,
    PlanDocumentSerializer,
    PmtInfoSerializer,
    PmtMethodSerializer,
    PmtPenaltySerializer,
    PmtStudySerializer,
    PmtSummarySerializer,
    PmtWellSerializer,
    ResolutionSerializer,
    StateRevenueSerializer,
    TimelineEventSerializer,
)


class CanEditContracts(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name="Admin").exists()


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [CanEditContracts]


class ContractRelatedViewSet(viewsets.ModelViewSet):
    permission_classes = [CanEditContracts]

    def get_queryset(self):
        queryset = super().get_queryset()
        contract_id = self.request.query_params.get("contract") or self.request.query_params.get("contract_id")
        if contract_id and hasattr(queryset.model, "contract"):
            queryset = queryset.filter(contract_id=contract_id)
        return queryset


class TimelineEventViewSet(ContractRelatedViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer


class LocationPointViewSet(ContractRelatedViewSet):
    queryset = LocationPoint.objects.all()
    serializer_class = LocationPointSerializer


class ContractorViewSet(ContractRelatedViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer


class ResolutionViewSet(ContractRelatedViewSet):
    queryset = Resolution.objects.all()
    serializer_class = ResolutionSerializer


class PmtSummaryViewSet(ContractRelatedViewSet):
    queryset = PmtSummary.objects.all()
    serializer_class = PmtSummarySerializer


class PmtWellViewSet(ContractRelatedViewSet):
    queryset = PmtWell.objects.all()
    serializer_class = PmtWellSerializer


class PmtInfoViewSet(ContractRelatedViewSet):
    queryset = PmtInfo.objects.all()
    serializer_class = PmtInfoSerializer


class PmtStudyViewSet(ContractRelatedViewSet):
    queryset = PmtStudy.objects.all()
    serializer_class = PmtStudySerializer


class PmtMethodViewSet(ContractRelatedViewSet):
    queryset = PmtMethod.objects.all()
    serializer_class = PmtMethodSerializer


class PmtPenaltyViewSet(ContractRelatedViewSet):
    queryset = PmtPenalty.objects.all()
    serializer_class = PmtPenaltySerializer


class NationalContentRuleViewSet(ContractRelatedViewSet):
    queryset = NationalContentRule.objects.all()
    serializer_class = NationalContentRuleSerializer


class PlanDocumentViewSet(ContractRelatedViewSet):
    queryset = PlanDocument.objects.all()
    serializer_class = PlanDocumentSerializer


class PlanActivityViewSet(viewsets.ModelViewSet):
    queryset = PlanActivity.objects.all()
    serializer_class = PlanActivitySerializer
    permission_classes = [CanEditContracts]


class InvestmentViewSet(ContractRelatedViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer


class StateRevenueViewSet(ContractRelatedViewSet):
    queryset = StateRevenue.objects.all()
    serializer_class = StateRevenueSerializer


class GeologicalDataViewSet(ContractRelatedViewSet):
    queryset = GeologicalData.objects.all()
    serializer_class = GeologicalDataSerializer


def as_float(value):
    return float(value or 0)


class ContractDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        contracts = Contract.objects.all()
        totals = contracts.aggregate(
            superficie=Sum("superficie_km2"),
            pozos_comprometidos=Sum("pozos_comprometidos"),
            pozos_terminados=Sum("pozos_terminados"),
        )
        investments = Investment.objects.aggregate(total=Sum("monto_ejercido_usd"))
        revenues = StateRevenue.objects.aggregate(
            total_mxn=Sum("monto_pagado_mxn"),
            total_usd=Sum("monto_pagado_usd"),
        )

        top_investments = (
            Investment.objects.values("contract_id")
            .annotate(total=Sum("monto_ejercido_usd"))
            .order_by("-total")[:5]
        )
        top_revenues = (
            StateRevenue.objects.values("contract_id")
            .annotate(total=Sum("monto_pagado_mxn"))
            .order_by("-total")[:5]
        )

        return Response(
            {
                "total_contracts": contracts.count(),
                "active_contracts": contracts.filter(estatus__icontains="Vigente").count(),
                "surface_km2": as_float(totals["superficie"]),
                "committed_wells": as_float(totals["pozos_comprometidos"]),
                "completed_wells": as_float(totals["pozos_terminados"]),
                "investment_usd": as_float(investments["total"]),
                "revenue_mxn": as_float(revenues["total_mxn"]),
                "revenue_usd": as_float(revenues["total_usd"]),
                "by_status": list(contracts.values("estatus").annotate(count=Count("contract_id")).order_by("-count")),
                "by_modality": list(contracts.values("modalidad").annotate(count=Count("contract_id")).order_by("-count")),
                "by_reservoir": list(contracts.values("tipo_yacimiento").annotate(count=Count("contract_id")).order_by("-count")),
                "top_investments": list(top_investments),
                "top_revenues": list(top_revenues),
            }
        )
