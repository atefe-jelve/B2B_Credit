from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from .models import Account, CreditTransaction
from .serializers import RechargeSerializer


class AccountViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = Account.objects.get(pk=pk)
        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def recharge(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_id = serializer.validated_data['account_id']
        amount = serializer.validated_data['amount']
        reference = serializer.validated_data['reference_number']

        account = Account.objects.select_for_update().get(id=account_id)

        # Log transaction and update balance
        CreditTransaction.objects.create(
            account=account,
            amount=amount,
            transaction_type=CreditTransaction.RECHARGE,
            reference_number=reference
        )
        account.current_balance += amount
        account.save()

        return Response({'message': 'Recharge successful', 'new_balance': account.current_balance})
