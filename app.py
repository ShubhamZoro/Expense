from flask import Flask, redirect, url_for, render_template, request, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from models import db, User, Expense, ExpenseSplit
from resources.user import UserResource
from resources.expense import ExpenseResource
from resources.balance import BalanceSheetResource
import csv
from io import StringIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='in.shubhamshekhar@gmail.com'
app.config['MAIL_PASSWORD']=
app.config['MAIL_DEFAULT_SENDER']='in.shubhamshekhar@gmail.com'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True


db.init_app(app)
migrate = Migrate(app, db)

mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

api = Api(app)
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(ExpenseResource, '/expenses', '/expenses/<int:user_id>')
api.add_resource(BalanceSheetResource, '/balance-sheet')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_verification_email(user_email):
    token = s.dumps(user_email, salt='email-confirm')
    link = url_for('confirm_email', token=token, _external=True)
    msg = Message('Confirm Your Email', recipients=[user_email])
    msg.body = f'Your link is {link}'
    mail.send(msg)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        return '<h1>The confirmation link is invalid or has expired.</h1>'
    user = User.query.filter_by(email=email).first_or_404()
    user.is_confirmed = True
    db.session.commit()
    flash('Your account has been confirmed. Thank you!')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        if not user.is_confirmed:
            flash('Please confirm your email first.')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Email already registered')
            return redirect(url_for('register'))
        new_user = User(email=email, name=name, mobile_number=mobile_number)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        send_verification_email(email)
        flash('A confirmation email has been sent to your email address.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@login_required
def index():
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total_expenses = sum(expense.amount for expense in user_expenses)
    return render_template('index.html', total_expenses=total_expenses, expenses=user_expenses)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        method = request.form['method']
        description = request.form.get('description')
        participants = request.form['participants'].split(',')

        # Create a new expense record
        new_expense = Expense(amount=amount, method=method, description=description, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()

        # Handle the split logic based on the method
        for participant in participants:
            user = User.query.filter_by(email=participant.strip()).first()
            if user:
                if method == 'equal':
                    split_amount = amount / len(participants)
                elif method == 'exact':
                    split_amount = float(request.form[f'amount_{participant.strip()}'])
                elif method == 'percentage':
                    split_amount = amount * (float(request.form[f'percentage_{participant.strip()}']) / 100)
                new_split = ExpenseSplit(user_id=user.id, expense_id=new_expense.id, amount=split_amount)
                db.session.add(new_split)

        db.session.commit()
        flash('Expense added successfully')
        return redirect(url_for('index'))

    return render_template('add_expense.html')

@app.route('/balance_sheet_download')
@login_required
def balance_sheet_download():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Description', 'Total Amount', 'Method', 'Participant Name', 'Participant Email', 'Amount'])
    for expense in expenses:
        for split in expense.splits:
            participant = User.query.get(split.user_id)
            writer.writerow([expense.description, expense.amount, expense.method, participant.name, participant.email, split.amount])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=balance_sheet.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


if __name__ == '__main__':
    app.run(debug=True)
