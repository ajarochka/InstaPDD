from rest_framework import serializers


class PostReportSerializer(serializers.Serializer):
    created_at = serializers.CharField(source='period')
    order_count = serializers.IntegerField(default=0)
    total_sum = serializers.FloatField(default=0)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['total_sum'] = round(ret.get('total_sum', 0) / 100, 2)  # Convert to som
        return ret


class NewCustomerReportSerializer(serializers.Serializer):
    created_at = serializers.CharField(source='date_joined__date', allow_null=True)
    count = serializers.IntegerField(default=0)


class ActiveCustomerReportSerializer(serializers.Serializer):
    created_at = serializers.CharField(source='created_at__date', allow_null=True)
    count = serializers.IntegerField(default=0)


class CountSerializer(serializers.Serializer):
    count = serializers.IntegerField(default=0)


class PointSerializer(serializers.Serializer):
    earned = serializers.IntegerField(default=0)
    used = serializers.IntegerField(default=0)


class TopCustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='user_id')
    first_name = serializers.CharField(source='user__first_name')
    last_name = serializers.CharField(source='user__last_name')
    photo = serializers.CharField(source='user__photo')
    count = serializers.IntegerField()
