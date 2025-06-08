from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super-secret-key-12345'  # Замените на более безопасный ключ
app.config['SESSION_COOKIE_SECURE'] = False  # False для отладки, True для продакшена с HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Сессия 1 час

# === Подключение к PostgreSQL ===
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

# === Модели ===
class Position(db.Model):
    __tablename__ = 'Должность'
    id = db.Column('ID должности', db.Integer, primary_key=True)
    name = db.Column('Название должности', db.String(100), unique=True, nullable=False)

class Employee(db.Model):
    __tablename__ = 'Сотрудник'
    id = db.Column('ID сотрудника', db.Integer, primary_key=True)
    surname = db.Column('Фамилия', db.String(100))
    first_name = db.Column('Имя', db.String(100))
    patronymic = db.Column('Отчество', db.String(100))
    phone = db.Column('Телефон', db.String(20))
    email = db.Column('Почта', db.String(100), unique=True)
    hire_date = db.Column('Дата найма', db.Date)
    position_id = db.Column('ID должности', db.Integer, db.ForeignKey('Должность.ID должности'))
    password_hash = db.Column('Хэш пароля', db.String(128))
    position = db.relationship('Position', backref='employees')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Publisher(db.Model):
    __tablename__ = 'Издательство'
    __table_args__ = {'extend_existing': True}
    id = db.Column('ID издательства', db.Integer, primary_key=True)
    name = db.Column('Название издательства', db.String(100), nullable=False, unique=True)

class Theme(db.Model):
    __tablename__ = 'Тематика'
    id = db.Column('ID тематики', db.Integer, primary_key=True)
    name = db.Column('Название тематики', db.String(100), nullable=False, unique=True)

class Author(db.Model):
    __tablename__ = 'Автор'
    id = db.Column('ID автора', db.Integer, primary_key=True)
    surname = db.Column('Фамилия', db.String(100), nullable=False)
    name = db.Column('Имя', db.String(100), nullable=False)
    patronymic = db.Column('Отчество', db.String(100))

class Genre(db.Model):
    __tablename__ = 'Жанр'
    id = db.Column('ID жанра', db.Integer, primary_key=True)
    name = db.Column('Название жанра', db.String(100), nullable=False, unique=True)

class Book(db.Model):
    __tablename__ = 'Книга'
    id = db.Column('ID книги', db.Integer, primary_key=True)
    title = db.Column('Название', db.String(255), nullable=False)
    year = db.Column('Год издания', db.Integer)
    price = db.Column('Цена', db.Numeric(10, 2), nullable=False)
    image_url = db.Column('Изображение', db.String(255))
    description = db.Column('Описание', db.Text)
    publisher_id = db.Column('ID издательства', db.Integer, db.ForeignKey('Издательство.ID издательства'))
    theme_id = db.Column('ID тематики', db.Integer, db.ForeignKey('Тематика.ID тематики'))
    publisher = db.relationship('Publisher', backref='books')
    theme = db.relationship('Theme', backref='books')
    book_authors = db.relationship('BookAuthor', backref='book', cascade='all, delete-orphan')
    book_genres = db.relationship('BookGenre', backref='book', cascade='all, delete-orphan')
    book_locations = db.relationship('BookLocation', backref='book', lazy=True)

class BookLocation(db.Model):
    __tablename__ = 'Местоположение книги'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    location_id = db.Column('ID места', db.Integer, db.ForeignKey('Место хранения.ID места'), primary_key=True)
    quantity = db.Column('Количество экземпляров', db.Integer, nullable=False)
    location = db.relationship('Location', backref='book_locations')

class Location(db.Model):
    __tablename__ = 'Место хранения'
    id = db.Column('ID места', db.Integer, primary_key=True)
    name = db.Column('Название', db.String(100), nullable=False)
    capacity = db.Column('Вместимость', db.Integer, nullable=False)
    location = db.Column('Местоположение', db.String(150), nullable=False)
    location_type_id = db.Column('ID типа места хранения', db.Integer)

class BookAuthor(db.Model):
    __tablename__ = 'Книга_Автор'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    author_id = db.Column('ID автора', db.Integer, db.ForeignKey('Автор.ID автора'), primary_key=True)
    author = db.relationship('Author', backref='book_authors')

class BookGenre(db.Model):
    __tablename__ = 'Книга_Жанр'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    genre_id = db.Column('ID жанра', db.Integer, db.ForeignKey('Жанр.ID жанра'), primary_key=True)
    genre = db.relationship('Genre', backref='book_genres')

# === Маршруты ===
@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.url}, Session: {session.get('employee_id', 'None')}, Path: {request.path}, Full Session: {session}")

@app.route('/')
def index():
    app.logger.info(f"Index accessed, session: {session.get('employee_id', 'None')}")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        employee = Employee.query.filter_by(email=email).first()
        if employee and employee.check_password(password):
            session['employee_id'] = employee.id
            session['position'] = employee.position.name
            session.permanent = True
            app.logger.info(f"Login successful for {email}, role: {employee.position.name}, session: {session.get('employee_id')}")
            if employee.position.name == 'Системный администратор':
                return redirect(url_for('show_employees'))
            else:
                return redirect(url_for('show_books'))
        flash("Неверная почта или пароль")
        app.logger.warning(f"Failed login attempt for {email}")
    return render_template('login.html')

@app.route('/logout')
def logout():
    app.logger.info(f"Logout, session before clear: {session.get('employee_id', 'None')}")
    session.clear()
    flash("Вы успешно вышли из системы")
    return redirect(url_for('login'))

@app.route('/admin_main')
def show_employees():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to admin_main, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to admin_main for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Admin_main accessed by {session.get('employee_id')}")
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
        app.logger.error(f"Ошибка при загрузке учётных записей: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/employee/<int:employee_id>')
def employee_detail(employee_id):
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to employee_detail, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to employee_detail for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Employee_detail accessed by {session.get('employee_id')} for employee {employee_id}")
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
        employee = result.mappings().one_or_none()
        if not employee:
            flash("Сотрудник не найден")
            return redirect(url_for('show_employees'))
        return render_template('employee_detail.html', employee=employee)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки данных сотрудника: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500


@app.route('/index')
def show_books():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    try:
        # Проверка наличия данных в связанных таблицах
        if not Book.query.first():
            flash("В базе нет ни одной книги", "info")
            return render_template('index.html', books=[])

        books = Book.query.options(
            db.joinedload(Book.publisher),
            db.joinedload(Book.theme),
            db.joinedload(Book.book_authors).joinedload(BookAuthor.author),
            db.joinedload(Book.book_genres).joinedload(BookGenre.genre)
        ).all()

        books_data = []
        for book in books:
            try:
                authors = [f"{ba.author.surname} {ba.author.name}" for ba in book.book_authors]
                genres = [bg.genre.name for bg in book.book_genres]
                quantity = sum(bl.quantity for bl in book.book_locations)

                books_data.append({
                    "id": book.id,
                    "title": book.title,
                    "price": float(book.price),
                    "in_stock": quantity > 0,
                    "authors": ", ".join(authors) if authors else "Не указан",
                    "genres": ", ".join(genres) if genres else "Не указан",
                    "publisher": book.publisher.name if book.publisher else "Не указан",
                    "description": book.description or "",
                    "image_url": book.image_url if book.image_url else None

                })
            except Exception as e:
                app.logger.error(f"Ошибка обработки книги ID {book.id}: {str(e)}")
                continue

        return render_template('index.html', books=books_data)

    except Exception as e:
        app.logger.error(f"Ошибка загрузки книг: {str(e)}", exc_info=True)
        flash("Произошла ошибка при загрузке каталога книг")
        return render_template('index.html', books=[])

@app.route('/book_info/<int:book_id>')
def book_info(book_id):
    app.logger.info(f"Book_info accessed for book {book_id}, session: {session.get('employee_id', 'None')}")
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to book_info, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    try:
        book = Book.query.get_or_404(book_id)
        authors = [f"{a.author.surname} {a.author.name} {a.author.patronymic or ''}".strip() for a in book.book_authors if a.author]
        genres = [g.genre.name for g in book.book_genres if g.genre]
        quantity = BookLocation.query.filter_by(book_id=book.id).first().quantity if BookLocation.query.filter_by(book_id=book.id).first() else 0
        book_data = {
            "title": book.title,
            "price": float(book.price),
            "image_url": book.image_url if book.image_url and book.image_url.startswith('images/') else None,
            "theme": book.theme.name if book.theme else None,
            "author": ", ".join(authors) if authors else None,
            "genre": ", ".join(genres) if genres else None,
            "quantity": quantity,
            "publisher": book.publisher.name if book.publisher else None,
            "description": book.description if book.description else "Описание отсутствует"
        }
        return render_template('book_info.html', book=book_data)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки информации о книге: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/shelf')
def shelf():
    app.logger.info(f"Shelf accessed, session: {session.get('employee_id', 'None')}, full session: {session}")
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to shelf, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    try:
        return render_template('shelf.html')
    except Exception as e:
        app.logger.error(f"Ошибка загрузки стеллажей: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/publisher')
def show_publishers():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to publisher, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to publisher for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Publisher accessed by {session.get('employee_id')}")
    try:
        publishers = Publisher.query.all()
        return render_template('publisher.html', publishers=publishers)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки издательств: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/publisher/add', methods=['GET', 'POST'])
def add_publisher():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to add_publisher, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to add_publisher for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Add_publisher accessed by {session.get('employee_id')}")
    if request.method == 'POST':
        try:
            new_name = request.form['name']
            if not new_name:
                flash("Название издательства не может быть пустым")
                return render_template('add_publisher.html')
            new_publisher = Publisher(name=new_name)
            db.session.add(new_publisher)
            db.session.commit()
            flash("Издательство успешно добавлено")
            return redirect(url_for('show_publishers'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Ошибка при добавлении издательства: {str(e)}")
            flash("Произошла ошибка при добавлении издательства")
            return "Внутренняя ошибка сервера", 500
    return render_template('add_publisher.html')

@app.route('/publisher/edit/<int:publisher_id>', methods=['GET', 'POST'])
def edit_publisher(publisher_id):
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to edit_publisher, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to edit_publisher for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Edit_publisher accessed by {session.get('employee_id')} for publisher {publisher_id}")
    publisher = Publisher.query.get_or_404(publisher_id)
    if request.method == 'POST':
        try:
            new_name = request.form['name']
            if not new_name:
                flash("Название издательства не может быть пустым")
                return render_template('edit_publisher.html', publisher=publisher)
            publisher.name = new_name
            db.session.commit()
            flash("Издательство успешно обновлено")
            return redirect(url_for('show_publishers'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Ошибка при редактировании издательства: {str(e)}")
            flash("Произошла ошибка при редактировании")
            return "Внутренняя ошибка сервера", 500
    return render_template('edit_publisher.html', publisher=publisher)

@app.route('/publisher/delete/<int:publisher_id>')
def delete_publisher(publisher_id):
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to delete_publisher, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to delete_publisher for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Delete_publisher accessed by {session.get('employee_id')} for publisher {publisher_id}")
    try:
        publisher = Publisher.query.get_or_404(publisher_id)
        db.session.delete(publisher)
        db.session.commit()
        flash("Издательство успешно удалено")
        return redirect(url_for('show_publishers'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка при удалении издательства: {str(e)}")
        flash("Произошла ошибка при удалении")
        return "Внутренняя ошибка сервера", 500

@app.route('/genre')
def show_genres():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to show_genres, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to show_genres for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Show_genres accessed by {session.get('employee_id')}")
    try:
        genres = Genre.query.all()
        return render_template('genre.html', genres=genres)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки жанров: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/theme')
def show_themes():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to show_themes, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to show_themes for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Show_themes accessed by {session.get('employee_id')}")
    try:
        themes = Theme.query.all()
        return render_template('theme.html', themes=themes)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки тематик: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

@app.route('/author')
def show_authors():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to show_authors, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to show_authors for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Show_authors accessed by {session.get('employee_id')}")
    try:
        authors = Author.query.all()
        return render_template('author.html', authors=authors)
    except Exception as e:
        app.logger.error(f"Ошибка загрузки авторов: {str(e)}")
        flash("Произошла ошибка при загрузке данных")
        return "Внутренняя ошибка сервера", 500

# === Поиск (опционально) ===
@app.route('/search_users', methods=['GET'])
def search_users():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to search_users, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to search_users for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Search_users accessed by {session.get('employee_id')}")
    query = request.args.get('query', '')
    try:
        sql = text('''
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
            WHERE s."Фамилия" ILIKE :query OR s."Имя" ILIKE :query OR s."Почта" ILIKE :query
            ORDER BY s."ID сотрудника"
            LIMIT 50
        ''')
        result = db.session.execute(sql, {'query': f'%{query}%'})
        employees = [dict(row) for row in result.mappings()]
        return render_template('admin_main.html', employees=employees, search_query=query)
    except Exception as e:
        app.logger.error(f"Ошибка при поиске: {str(e)}")
        flash("Произошла ошибка при поиске")
        return redirect(url_for('show_employees'))

# === Резервное копирование (заглушка) ===
@app.route('/backup')
def backup():
    if 'employee_id' not in session:
        app.logger.warning(f"Access denied to backup, no session, redirecting to login")
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    if session.get('position') != 'Системный администратор':
        app.logger.warning(f"Access denied to backup for {session.get('employee_id')}, not admin, redirecting to show_books")
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books'))
    app.logger.info(f"Backup accessed by {session.get('employee_id')}")
    flash("Функция резервного копирования пока не реализована")
    return redirect(url_for('show_employees'))


@app.route('/cart')
def cart():
    if 'employee_id' not in session:
        return redirect(url_for('login'))

    # Здесь должна быть логика получения данных корзины
    # Пока просто вернем шаблон
    return render_template('cart.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создает только новые таблицы, если они не существуют
    app.run(debug=True, port=5001)

