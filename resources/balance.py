from flask_restful import Resource
from flask_login import login_required, current_user
from models import db, Expense, ExpenseSplit, User
import csv
from io import StringIO
from flask import make_response

class BalanceSheetResource(Resource):
    @login_required
    def get(self):
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        response = {'total_expenses': 0, 'details': []}

        for expense in expenses:
            splits = [{'user': User.query.get(split.user_id).name, 'amount': split.amount} for split in expense.splits]
            expense_info = {
                'description': expense.description,
                'total_amount': expense.amount,
                'method': expense.method,
                'splits': splits
            }
            response['total_expenses'] += expense.amount
            response['details'].append(expense_info)

        return response

    @login_required
    def post(self):
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(['Description', 'Total Amount', 'Method', 'Participant', 'Amount'])
        for expense in expenses:
            for split in expense.splits:
                participant_name = User.query.get(split.user_id).name
                writer.writerow([expense.description, expense.amount, expense.method, participant_name, split.amount])

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=balance_sheet.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
