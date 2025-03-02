from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Account, CreditTransaction
from .serializers import RechargeSerializer, TransactionSerializer


class AccountViewSet(ViewSet):

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = Account.objects.get(pk=pk)
        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def recharge(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # this line , avoids 'race conditions' if multiple requests hit the same account at the same time
        account = Account.objects.select_for_update().get(id=serializer.validated_data['account_id'])

        # log this recharge
        CreditTransaction.objects.create(
            account=account,
            amount=serializer.validated_data['amount'],
            transaction_type=CreditTransaction.RECHARGE,
            reference_number=serializer.validated_data['reference_number']
        )

        # Updates the account balance
        account.current_balance += serializer.validated_data['amount']
        account.save()

        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def sale(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = Account.objects.select_for_update().get(id=serializer.validated_data['account_id'])

        # prevents overdraft
        if account.current_balance < serializer.validated_data['amount']:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        CreditTransaction.objects.create(
            account=account,
            amount=-serializer.validated_data['amount'],
            transaction_type=CreditTransaction.SALE,
            reference_number=serializer.validated_data['reference_number']
        )
        account.current_balance -= serializer.validated_data['amount']
        account.save()

        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        queryset = CreditTransaction.objects.all()
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
