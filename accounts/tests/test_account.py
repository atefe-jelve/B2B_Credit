
from rest_framework.test import APITestCase
from accounts.models import Account
from concurrent.futures import ThreadPoolExecutor

class AccountTests(APITestCase):

    def setUp(self):
        #  build sellers for test
        self.seller1 = Account.objects.create(reseller_name='Seller 1', current_balance=0)
        self.seller2 = Account.objects.create(reseller_name='Seller 2', current_balance=0)

        #  build seller for parallel test
        self.parallel_account = Account.objects.create(reseller_name='Parallel Seller', current_balance=10000)

    #### -------------------- Simple Case Test --------------------

    def recharge_account(self, account, amount, reference_number):
        response = self.client.post('/api/accounts/recharge/', {
            'account_id': account.id,
            'amount': amount,
            'reference_number': reference_number
        })
        self.assertEqual(response.status_code, 200)

    def sale_from_account(self, account, amount, reference_number):
        response = self.client.post('/api/accounts/sale/', {
            'account_id': account.id,
            'amount': amount,
            'reference_number': reference_number
        })
        return response

    def test_simple_case(self):
        # 10 charging times for each seller
        for i in range(10):
            self.recharge_account(self.seller1, 1000, f"RECHARGE1_{i}")
            self.recharge_account(self.seller2, 1000, f"RECHARGE2_{i}")

        # 1000 sales units from seller1 account
        sale_response = self.sale_from_account(self.seller1, 1000, "SALE_1")
        self.assertEqual(sale_response.status_code, 200)

        # Checking account balances
        self.seller1.refresh_from_db()
        self.seller2.refresh_from_db()

        self.assertEqual(self.seller1.current_balance, 9000)
        self.assertEqual(self.seller2.current_balance, 10000)

    #### -------------------- Parallel Load Test --------------------

    def parallel_sale_request(self, reference_number):
        response = self.client.post('/api/accounts/sale/', {
            'account_id': self.parallel_account.id,
            'amount': 500,
            'reference_number': reference_number
        })

        # If the balance is low, you may give 400, here we accept 200 or 400
        self.assertIn(response.status_code, [200, 400])

    def test_parallel_sales(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.parallel_sale_request, f"SALE_{i}")
                for i in range(20)
            ]
            for future in futures:
                future.result()

        # Checking that the balance is not negative
        self.parallel_account.refresh_from_db()
        self.assertLessEqual(self.parallel_account.current_balance, 10000)
        self.assertGreaterEqual(self.parallel_account.current_balance, 0)











