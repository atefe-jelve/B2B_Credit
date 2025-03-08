from rest_framework import serializers
from .models import Account, CreditTransaction

class RechargeSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reference_number = serializers.CharField(max_length=50)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = '__all__'
