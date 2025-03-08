from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Account, CreditTransaction
from .serializers import RechargeSerializer, TransactionSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db import IntegrityError


class AccountViewSet(ViewSet):
    # permission_classes = [IsAuthenticated]

    def balance(self, request, pk=None):

        try:
            account = Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=404)

        return Response({'balance': account.current_balance})


    @action(detail=False, methods=['post'], url_path='recharge')
    @transaction.atomic
    def recharge(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # this line , avoids 'race conditions' if multiple requests hit the same account at the same time
        try:
            account = Account.objects.select_for_update().get(id=serializer.validated_data['account_id'])
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=404)

        try:
            # log this recharge
            CreditTransaction.objects.create(
                account=account,
                amount=serializer.validated_data['amount'],
                transaction_type=CreditTransaction.RECHARGE,
                reference_number=serializer.validated_data['reference_number'],
            )
        except IntegrityError:
            return Response({'error': 'Reference number already exists. Please use a unique reference number.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Updates the account balance
        account.current_balance += serializer.validated_data['amount']
        account.save()

        # expected_balance = account.calculate_balance()
        # if expected_balance != account.current_balance:
        #     raise Exception("Accounting mismatch after sale!")

        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['post'], url_path='sale', url_name='sale')
    @transaction.atomic
    def sale(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            account = Account.objects.select_for_update().get(id=serializer.validated_data['account_id'])
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=404)

        # prevents overdraft
        if account.current_balance < serializer.validated_data['amount']:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CreditTransaction.objects.create(
                account=account,
                amount=-serializer.validated_data['amount'],
                transaction_type=CreditTransaction.SALE,
                reference_number=serializer.validated_data['reference_number'],
            )
        except IntegrityError:
            return Response({'error': 'Reference number already exists. Please use a unique reference number.'},
                            status=status.HTTP_400_BAD_REQUEST)

        account.current_balance -= serializer.validated_data['amount']
        account.save()

        # expected_balance = account.calculate_balance()
        # if expected_balance != account.current_balance:
        #     raise Exception("Accounting mismatch after sale!")

        return Response({'balance': account.current_balance})

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        queryset = CreditTransaction.objects.all()
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)
