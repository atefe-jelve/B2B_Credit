from django.db import models

class Account(models.Model):
    reseller_name = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CreditTransaction(models.Model):
    RECHARGE = 'RECHARGE'
    SALE = 'SALE'
    TRANSACTION_TYPES = [
        (RECHARGE, 'Recharge'),
        (SALE, 'Sale'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
