from django.contrib import admin
from .models import Account, CreditTransaction

admin.site.register(Account)
admin.site.register(CreditTransaction)
