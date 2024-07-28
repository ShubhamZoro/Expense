from flask_restful import Resource, reqparse
from flask_login import login_required, current_user
from models import db, Expense, User, ExpenseSplit

class ExpenseResource(Resource):
    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True)
        parser.add_argument('method', required=True)
        parser.add_argument('description')
        parser.add_argument('splits', type=dict, action='append', required=True)
        args = parser.parse_args()

        user = User.query.get_or_404(current_user.id)
        new_expense = Expense(amount=args['amount'], method=args['method'], description=args.get('description'), user=user)
        db.session.add(new_expense)
        db.session.commit()

        total_split = 0
        for split in args['splits']:
            split_user = User.query.get_or_404(split['user_id'])
            split_amount = split['amount']
            if args['method'] == 'percentage':
                split_amount = (split['amount'] / 100) * args['amount']
            total_split += split_amount
            new_split = ExpenseSplit(user=split_user, expense=new_expense, amount=split_amount)
            db.session.add(new_split)

        if args['method'] == 'percentage' and total_split != args['amount']:
            db.session.rollback()
            return {'message': 'Total percentages must add up to 100%'}, 400

        db.session.commit()
        return {'message': 'Expense added successfully'}, 201

    @login_required
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        expenses = [{'amount': exp.amount, 'method': exp.method, 'description': exp.description} for exp in user.expenses]
        return {'expenses': expenses}
