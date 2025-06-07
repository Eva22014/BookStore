from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from urllib.parse import quote_plus

app = Flask(__name__)

# Конфигурация подключения к БД
password = ""
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

@app.route('/')
def index():
    return '''
    <h1>📚 BookStore</h1>
    <p><a href="/admin_main">Перейти к сотрудникам</a></p>
    '''

@app.route('/admin_main')
def show_employees():
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
        return f"Ошибка загрузки данных: {str(e)}", 500

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


if __name__ == '__main__':
    app.run(debug=True)