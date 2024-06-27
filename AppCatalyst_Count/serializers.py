# serializers.py

from rest_framework import serializers
from .models import Company_data

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company_data
        fields = '__all__'

class QueryParamsSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    employees_from = serializers.IntegerField(required=False, allow_null=True)
    employees_to = serializers.IntegerField(required=False, allow_null=True)
    industry = serializers.CharField(required=False, allow_blank=True)
    year_founded = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
