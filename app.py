from flask import Flask, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired
from icecream import ic
import locale
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super_secret_key_28"
bootstrap = Bootstrap5(app)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///card-database.db"
db = SQLAlchemy()
db.init_app(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_name = db.Column(db.String, unique=True, nullable=False)
    card_limit = db.Column(db.Float, nullable=False)
    card_balance = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
class Utilization(FlaskForm):
    card_name = StringField('Card Name', validators=[DataRequired()])
    card_limit = DecimalField('Balance', validators=[DataRequired()])
    balance = DecimalField('Balance', validators=[DataRequired()])
    interest = DecimalField('Interest', validators=[DataRequired()])
    submit = SubmitField('Add')


credit_cards = {"TikTok": ['11700', '9883', '29'],
                "C1": ['21000','20494','23.3'],
                "AX": ['15000', '12317.48', '27.99']}


@app.route('/', methods=['GET', 'POST'])
def index():
    with app.app_context():
        result = db.session.execute(db.select(Card).order_by(Card.card_name))
        my_cards = result.scalars().all()
        count = len(my_cards)
    return render_template('index.html', cards=my_cards, count=count)


@app.route('/add', methods=['GET', 'POST'])
def add_card():
    form = Utilization()
    if request.method == 'GET':
        return render_template('add.html', form=form)
    if request.method == 'POST':
        card_name = request.form["card_name"]
        card_limit = request.form["card_limit"]
        balance = request.form["balance"]
        interest = request.form["interest"]
        # credit_cards[card_name] = [card_limit, balance, interest]
        with app.app_context():
            new_card = Card(card_name=card_name, card_limit=card_limit, card_balance=balance, interest_rate=interest)
            db.session.add(new_card)
            db.session.commit()
        return redirect(url_for('index'))



@app.route('/plan/<card_id>')
def payment_plan(card_id):
    current_card = db.session.execute(db.select(Card).where(Card.id == card_id)).scalar()
    # limit = int(credit_cards[card_id][0])
    # balance = float(credit_cards[card_id][1])
    # interest = float(credit_cards[card_id][2])
    name = current_card.card_name
    limit = current_card.card_limit
    balance = current_card.card_balance
    interest = current_card.interest_rate
    utilization = (balance / limit) * 100
    current_interest = (balance * (interest / 100)) / 12
    goal_75 = limit * .75
    goal_49 = limit * .49
    goal_29 = limit * .29
    goal_9 = limit * .09
    if utilization > 75:
        goal = "75%"
        payment = (balance - goal_75) + current_interest
    elif utilization > 49:
        goal = "49%"
        payment = (balance - goal_49) + current_interest
    elif utilization > 29:
        goal = "29%"
        payment = (balance - goal_29) + current_interest
    elif utilization > 9:
        goal = "9%"
        payment = (balance - goal_9) + current_interest
    else:
        goal = "0"
        payment = balance
    details = [name, locale.currency(limit), locale.currency(balance), interest]
    plan = [round(utilization, 2), locale.currency(current_interest), goal, locale.currency(payment)]
    targets = [locale.currency(goal_75),locale.currency(goal_49), locale.currency(goal_29), locale.currency(goal_9)]
    return render_template('payment_plan.html', details=details, plan=plan, target=targets)


if __name__ == '__main__':
    app.run()
