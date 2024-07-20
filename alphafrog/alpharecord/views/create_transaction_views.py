import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.transactions import FundTransactionRecord


@csrf_exempt
def create_normal_transaction(request):
    try:
        if request.method == 'POST':
            analyzed_records = json.loads(request.body)
            transactions_to_create = []
            for record in analyzed_records:
                transaction_time = datetime.strptime(record['time'], '%Y/%m/%d %H:%M:%S')
                transaction_record = FundTransactionRecord(
                    transaction_time=transaction_time,
                    transaction_platform=record['platform'],
                    transaction_ts_code=record['ts_code'],
                    transaction_fund_name=record['fund_database_name'],
                    transaction_amount=record['amount'],
                    transaction_nav=record['nav'],
                    transaction_shares=record['shares'],
                    transaction_fee=record['fee'],
                    transaction_type=record['type']
                )
                transactions_to_create.append(transaction_record)
            FundTransactionRecord.objects.bulk_create(transactions_to_create)

            return JsonResponse({'message': 'Records created successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'Error: {e}'}, status=500)