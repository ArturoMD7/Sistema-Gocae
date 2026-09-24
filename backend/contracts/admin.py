from django.contrib import admin

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


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_id", "modalidad", "operador_principal", "tipo_yacimiento", "estatus")
    search_fields = ("contract_id", "operador_principal", "estatus")
    list_filter = ("modalidad", "tipo_yacimiento", "estatus")


for model in (
    TimelineEvent,
    LocationPoint,
    Contractor,
    Resolution,
    PmtSummary,
    PmtWell,
    PmtInfo,
    PmtStudy,
    PmtMethod,
    PmtPenalty,
    NationalContentRule,
    PlanDocument,
    PlanActivity,
    Investment,
    StateRevenue,
    GeologicalData,
):
    admin.site.register(model)
