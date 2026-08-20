from rest_framework import serializers

from .models import Destination


class OperationsDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ("id", "name", "slug", "is_active", "sort_order")
