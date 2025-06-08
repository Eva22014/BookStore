from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask import flash

app = Flask(__name__)

# Конфигурация подключения к БД
password = "518695"
encoded_password = quote_plus(password)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{encoded_password}@localhost:5432/bookstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 5,
    'max_overflow': 2,
    'pool_recycle': 300
}

db = SQLAlchemy(app)

# === Главная страница — теперь редирект на /login ===
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/admin_main')
def show_employees():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    try:
        query = text('''
            SELECT 
                s."ID сотрудника",
                s."Фамилия" AS last_name,
                s."Имя" AS first_name,
                s."Отчество" AS middle_name,
                s."Телефон" AS phone,
                s."Почта" AS email,
                d."Название должности" AS position_name,
                s."Дата найма" AS hire_date
            FROM "Сотрудник" s
            JOIN "Должность" d ON s."ID должности" = d."ID должности"
            ORDER BY s."ID сотрудника"
            LIMIT 50
        ''')

        result = db.session.execute(query)
        employees = [dict(row) for row in result.mappings()]
        return render_template('admin_main.html', employees=employees)

    except Exception as e:
        app.logger.error(f"Ошибка при загрузке учётных записей: {str(e)}", exc_info=True)
        return "Внутренняя ошибка сервера", 500

@app.route('/employee/<int:employee_id>')
def employee_detail(employee_id):
    try:
        query = text('''
            SELECT 
                s."ID сотрудника",
                s."Фамилия" AS last_name,
                s."Имя" AS first_name,
                s."Отчество" AS middle_name,
                s."Телефон" AS phone,
                s."Почта" AS email,
                d."Название должности" AS position_name,
                s."Дата найма" AS hire_date
            FROM "Сотрудник" s
            JOIN "Должность" d ON s."ID должности" = d."ID должности"
            WHERE s."ID сотрудника" = :employee_id
        ''')
        result = db.session.execute(query, {'employee_id': employee_id})
        employee = result.mappings().one()
        return render_template('employee_detail.html', employee=employee)
    except Exception as e:
        return f"Ошибка загрузки данных сотрудника: {str(e)}", 500
class Position(db.Model):
    __tablename__ = 'Должность'
    id = db.Column('ID должности', db.Integer, primary_key=True)
    name = db.Column('Название должности', db.String(100), unique=True, nullable=False)

# === Модель для таблицы "Издательство" ===
class Publisher(db.Model):
    __tablename__ = 'Издательство'
    id = db.Column('ID издательства', db.Integer, primary_key=True)
    name = db.Column('Название издательства', db.String(100), nullable=False, unique=True)


# === Страница со списком издательств ===
@app.route('/publisher')
def show_publishers():
    try:
        publishers = Publisher.query.all()
        return render_template('publisher.html', publishers=publishers)
    except Exception as e:
        return f"Ошибка загрузки данных: {str(e)}", 500


# === Добавление издательства ===
@app.route('/publisher/add', methods=['GET', 'POST'])
def add_publisher():
    if request.method == 'POST':
        try:
            new_name = request.form['name']
            new_publisher = Publisher(name=new_name)
            db.session.add(new_publisher)
            db.session.commit()
            return redirect(url_for('show_publishers'))
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при добавлении: {str(e)}", 500
    return render_template('add_publisher.html')


# === Редактирование издательства ===
@app.route('/publisher/edit/<int:publisher_id>', methods=['GET', 'POST'])
def edit_publisher(publisher_id):
    publisher = Publisher.query.get_or_404(publisher_id)

    if request.method == 'POST':
        try:
            publisher.name = request.form['name']
            db.session.commit()
            return redirect(url_for('show_publishers'))
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при редактировании: {str(e)}", 500

    return render_template('edit_publisher.html', publisher=publisher)


# === Удаление издательства ===
@app.route('/publisher/delete/<int:publisher_id>')
def delete_publisher(publisher_id):
    try:
        publisher = Publisher.query.get_or_404(publisher_id)
        db.session.delete(publisher)
        db.session.commit()
        return redirect(url_for('show_publishers'))
    except Exception as e:
        db.session.rollback()
        return f"Ошибка при удалении: {str(e)}", 50

class Genre(db.Model):
    __tablename__ = 'Жанр'
    id = db.Column('ID жанра', db.Integer, primary_key=True)
    name = db.Column('Название жанра', db.String(100), nullable=False, unique=True)


class Theme(db.Model):
    __tablename__ = 'Тематика'
    id = db.Column('ID тематики', db.Integer, primary_key=True)
    name = db.Column('Название тематики', db.String(100), nullable=False, unique=True)


class Author(db.Model):
    __tablename__ = 'Автор'
    id = db.Column('ID автора', db.Integer, primary_key=True)
    surname = db.Column('Фамилия', db.String(100), nullable=False)
    first_name = db.Column('Имя', db.String(100), nullable=False)
    patronymic = db.Column('Отчество', db.String(100))


class Employee(db.Model):
    __tablename__ = 'Сотрудник'

    id = db.Column('ID сотрудника', db.Integer, primary_key=True)
    surname = db.Column('Фамилия', db.String(100))
    first_name = db.Column('Имя', db.String(100))
    patronymic = db.Column('Отчество', db.String(100))
    phone = db.Column('Телефон', db.String(20))
    email = db.Column('Почта', db.String(100), unique=True)
    hire_date = db.Column('Дата найма', db.Date)
    position_id = db.Column('ID должности', db.Integer,
                            db.ForeignKey('Должность.ID должности'))  # Удалили лишние кавычки
    password_hash = db.Column('Хэш пароля', db.String(128))

    position = db.relationship('Position', backref='employees')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
@app.route('/genre')
def show_genres():
    try:
        genres = Genre.query.all()
        return render_template('genre.html', genres=genres)
    except Exception as e:
        return f"Ошибка загрузки данных: {str(e)}", 500


@app.route('/theme')
def show_themes():
    try:
        themes = Theme.query.all()
        return render_template('theme.html', themes=themes)
    except Exception as e:
        return f"Ошибка загрузки данных: {str(e)}", 500


@app.route('/author')
def show_authors():
    try:
        authors = Author.query.all()
        return render_template('author.html', authors=authors)
    except Exception as e:
        return f"Ошибка загрузки данных: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        employee = Employee.query.filter(Employee.email == email).first()

        if employee and employee.check_password(password):
            session['employee_id'] = employee.id
            session['position'] = employee.position.name

            # Проверка роли
            if employee.position.name == 'Системный администратор':
                return redirect(url_for('show_employees'))  # Страница для админа
            else:
                return redirect(url_for('user_dashboard'))  # Для всех остальных

        flash("Неверная почта или пароль")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
@app.route('/dashboard')
def user_dashboard():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    return "<h1>Вы успешно авторизовались</h1><p>Это страница для всех, кроме администратора.</p>"

app.secret_key = 'super-secret-key-12345'

if __name__ == '__main__':
    app.run(debug=True)



