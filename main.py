import json

from flask import Flask, render_template, redirect, request, make_response, jsonify, send_file, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, login_manager
from sqlalchemy import func, cast, String, or_

from forms.user import RegisterForm, LoginForm
from data.users import User
from data.compositions import MainTable
from data import db_session, composition_api


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
sort_by_class = False
sort_by_author = False

def main():
    db_session.global_init("db/library.db")
    app.register_blueprint(composition_api.blueprint)
    login_manager.login_view = 'login'
    app.run(port=8080, host='127.0.0.1')


# просто коментарий



@app.route("/")
@app.route("/index")
def index():

    db_sess = db_session.create_session()
    params = {}
    if current_user.is_authenticated:
        params['molodec'] = True
    else:
        params['molodec'] = False
    params['title'] = 'Дневник читателя'

    # Получение уникальных значений для фильтров
    unique_manifacturers = sorted([el[0] for el in db_sess.query(MainTable.Manufacturer).distinct().all()])
    unique_products = sorted([el[0] for el in db_sess.query(MainTable.Product).distinct().all()])
    unique_prices = sorted([el[0] for el in db_sess.query(MainTable.Price).distinct().all()])
    unique_min_quantities = sorted([el[0] for el in db_sess.query(MainTable.Min_quantity).distinct().all()])
    unique_types = sorted([el[0] for el in db_sess.query(MainTable.Type).distinct().all()])

    print(*[(el, type(el)) for el in unique_min_quantities])

    # Фильтрация при наличии параметров фильтров
    filter_product = request.args.get('filter_product')
    filter_price = request.args.get('filter_price')
    filter_min_quantity = request.args.get('filter_min_quantity')
    filter_manufacturer = request.args.get('filter_manufacturer')
    filter_type = request.args.get('filter_type')

    compositions = db_sess.query(MainTable)

    if filter_product:
        compositions = compositions.filter(MainTable.Product == filter_product)
        params["filter_product"] = filter_product
    if filter_price:
        compositions = compositions.filter(MainTable.Price == filter_price)
        params["filter_price"] = filter_price
    if filter_min_quantity:
        compositions = compositions.filter(MainTable.Min_quantity == filter_min_quantity)
        params["filter_min_quantity"] = filter_min_quantity
    if filter_manufacturer:
        compositions = compositions.filter(MainTable.Manufacturer == filter_manufacturer)
        params["filter_manufacturer"] = filter_manufacturer
    if filter_type:
        compositions = compositions.filter(MainTable.Type == filter_type)
        params["filter_type"] = filter_type

    # Загружаем только отфильтрованные произведения
    params["compositions"] = compositions.all()

    params["unique_manifacturers"] = unique_manifacturers
    params["unique_products"] = unique_products
    params["unique_prices"] = unique_prices
    params["unique_min_quantities"] = unique_min_quantities
    params["unique_types"] = unique_types

    return render_template('index.html', **params)


@app.route("/search", methods=['post', 'get'])
def search():
    if request.method == 'POST':
        print("1")
        search_value = request.form['search_value']  # запрос к данным формы
        db_sess = db_session.create_session()
        params = {}
        compositions = []
        if current_user.is_authenticated:
            params['molodec'] = True
        else:
            params['molodec'] = False
        params['title'] = 'Дневник читателя'



        compositions = db_sess.query(MainTable).filter(or_(
            *[func.lower(cast(column, String)).like(f'%{search_value}%') for column in
              MainTable.__table__.columns])).all()



        print(MainTable)
        params["compositions"] = compositions
        return render_template('index.html', **params)

"""
@app.route('/<name>')
def about_composition(name):
    params = {}
    db_sess = db_session.create_session()
    composition = db_sess.query(MainTable).filter(MainTable.Name == name).all()
    try:
        params["composition"] = composition[0]
        return render_template("composition.html", **params)
    except IndexError:
        params["composition"] = composition
        return render_template("composition.html", **params)
"""

@app.route("/about")
def about_app():
    return render_template("about_app.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/rate', methods=['GET', 'POST'])
@login_required
def rate_product():
    params = {}
    db_sess = db_session.create_session()
    unique_manifacturers = sorted([el[0] for el in db_sess.query(MainTable.Manufacturer).distinct().all()])
    params["unique_manifacturers"] = unique_manifacturers
    if request.method == 'POST':

        manufacturer = request.form['manufacturer']
        rating = int(request.form['rating'])

        db_sess = db_session.create_session()
        composition = db_sess.query(MainTable).filter(MainTable.Manufacturer == manufacturer).first()

        if composition:
            composition.Rating_sum += rating
            composition.Rating_count += 1
            composition.Rating_avg = composition.Rating_sum / composition.Rating_count

            db_sess.commit()
        return redirect("/")
    return render_template("rate.html", **params)


if __name__ == '__main__':
    main()
