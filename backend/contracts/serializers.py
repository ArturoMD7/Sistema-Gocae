from rest_framework import serializers

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


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class TimelineEventSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = TimelineEvent
        fields = "__all__"


class LocationPointSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = LocationPoint
        fields = "__all__"


class ContractorSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = Contractor
        fields = "__all__"


class ResolutionSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = Resolution
        fields = "__all__"


class PmtSummarySerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtSummary
        fields = "__all__"


class PmtWellSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtWell
        fields = "__all__"


class PmtInfoSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtInfo
        fields = "__all__"


class PmtStudySerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtStudy
        fields = "__all__"


class PmtMethodSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtMethod
        fields = "__all__"


class PmtPenaltySerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PmtPenalty
        fields = "__all__"


class NationalContentRuleSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = NationalContentRule
        fields = "__all__"


class PlanDocumentSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = PlanDocument
        fields = "__all__"


class PlanActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanActivity
        fields = "__all__"


class InvestmentSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = Investment
        fields = "__all__"


class StateRevenueSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = StateRevenue
        fields = "__all__"


class GeologicalDataSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field="contract_id", queryset=Contract.objects.all())

    class Meta:
        model = GeologicalData
        fields = "__all__"
