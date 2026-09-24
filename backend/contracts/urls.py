from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ContractDashboardView,
    ContractViewSet,
    ContractorViewSet,
    GeologicalDataViewSet,
    InvestmentViewSet,
    LocationPointViewSet,
    NationalContentRuleViewSet,
    PlanActivityViewSet,
    PlanDocumentViewSet,
    PmtInfoViewSet,
    PmtMethodViewSet,
    PmtPenaltyViewSet,
    PmtStudyViewSet,
    PmtSummaryViewSet,
    PmtWellViewSet,
    ResolutionViewSet,
    StateRevenueViewSet,
    TimelineEventViewSet,
)

router = DefaultRouter()
router.register(r"contracts", ContractViewSet)
router.register(r"timeline-events", TimelineEventViewSet)
router.register(r"location-points", LocationPointViewSet)
router.register(r"contractors", ContractorViewSet)
router.register(r"resolutions", ResolutionViewSet)
router.register(r"pmt-summaries", PmtSummaryViewSet)
router.register(r"pmt-wells", PmtWellViewSet)
router.register(r"pmt-info", PmtInfoViewSet)
router.register(r"pmt-studies", PmtStudyViewSet)
router.register(r"pmt-methods", PmtMethodViewSet)
router.register(r"pmt-penalties", PmtPenaltyViewSet)
router.register(r"national-content-rules", NationalContentRuleViewSet)
router.register(r"plan-documents", PlanDocumentViewSet)
router.register(r"plan-activities", PlanActivityViewSet)
router.register(r"investments", InvestmentViewSet)
router.register(r"state-revenues", StateRevenueViewSet)
router.register(r"geological-data", GeologicalDataViewSet)

urlpatterns = [
    path("contracts/dashboard/", ContractDashboardView.as_view(), name="contracts-dashboard"),
    path("", include(router.urls)),
]
