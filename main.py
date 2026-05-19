from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask import Flask, render_template, url_for, redirect, flash, request
from data.register import RegistrationForm
from data.purum import db
from data.users import User
from werkzeug.security import generate_password_hash
from data.db_session import create_session, global_init
from flask_login import current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "db", "worlds.db")}'
global_init('db/worlds.db')

db.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    title = 'Star Silent Story'
    return render_template('base.html', title=title)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = db.session.query(User).filter(User.email == email).first()
        if existing_user:
            # Если пользователь найден, выводим ошибку
            flash('Email уже занят.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=username,
            email=email,
            hashed_password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
    return render_template('register.html', title='Регистрация', form=form)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    session = create_session()
    user = session.query(User).filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user, remember=True)
        flash('Вы успешно вошли в систему!')
        return redirect(url_for('universes'))
    else:
        flash('Неверный email или пароль. Попробуйте еще раз.')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))

@app.route('/worlds')
def universes():
    return render_template('worlds.html')

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


if __name__ == '__main__':
    app.run(debug=True)
