from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, CheckConstraint  # Добавлен импорт CheckConstraint
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
# ... (остальной код остается без изменений)

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

# === Модели (оставляем только необходимые) ===
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

class Cart(db.Model):
    __tablename__ = 'Корзина'
    id = db.Column('ID корзины', db.Integer, primary_key=True)
    employee_id = db.Column('ID сотрудника', db.Integer, db.ForeignKey('Сотрудник.ID сотрудника'), unique=True)
    created_at = db.Column('Дата создания', db.DateTime, default=db.func.current_timestamp())
    status = db.Column('Статус', db.String(20), default='Активна')

class CartItem(db.Model):
    __tablename__ = 'Содержимое корзины'
    cart_id = db.Column('ID корзины', db.Integer, db.ForeignKey('Корзина.ID корзины'), primary_key=True)
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    quantity = db.Column('Количество', db.Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('Количество > 0', name='check_quantity_positive'),
    )

# === Маршруты ===
@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.url}, Session: {session.get('employee_id', 'None')}, Path: {request.path}, Full Session: {session}")

@app.route('/')
def index():
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
            if employee.position.name == 'Системный администратор':
                return redirect(url_for('show_employees'))
            else:
                return redirect(url_for('show_books'))
        flash("Неверная почта или пароль")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Вы успешно вышли из системы")
    return redirect(url_for('login'))

@app.route('/admin_main')
def show_employees():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    query = text('''
        SELECT s."ID сотрудника", s."Фамилия" AS last_name, s."Имя" AS first_name, s."Отчество" AS middle_name,
               s."Телефон" AS phone, s."Почта" AS email, d."Название должности" AS position_name, s."Дата найма" AS hire_date
        FROM "Сотрудник" s JOIN "Должность" d ON s."ID должности" = d."ID должности"
        ORDER BY s."ID сотрудника" LIMIT 50
    ''')
    result = db.session.execute(query)
    employees = [dict(row) for row in result.mappings()]
    return render_template('admin_main.html', employees=employees)

@app.route('/employee/<int:employee_id>')
def employee_detail(employee_id):
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    query = text('''
        SELECT s."ID сотрудника", s."Фамилия" AS last_name, s."Имя" AS first_name, s."Отчество" AS middle_name,
               s."Телефон" AS phone, s."Почта" AS email, d."Название должности" AS position_name, s."Дата найма" AS hire_date
        FROM "Сотрудник" s JOIN "Должность" d ON s."ID должности" = d."ID должности"
        WHERE s."ID сотрудника" = :employee_id
    ''')
    result = db.session.execute(query, {'employee_id': employee_id})
    employee = result.mappings().one_or_none()
    if not employee:
        flash("Сотрудник не найден")
        return redirect(url_for('show_employees'))
    return render_template('employee_detail.html', employee=employee)

@app.route('/index')
def show_books():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    books = Book.query.options(
        db.joinedload(Book.publisher),
        db.joinedload(Book.theme),
        db.joinedload(Book.book_authors).joinedload(BookAuthor.author),
        db.joinedload(Book.book_genres).joinedload(BookGenre.genre)
    ).all()
    books_data = []
    book_locations = {bl.book_id: bl.quantity for bl in BookLocation.query.all()}
    for book in books:
        authors = [f"{ba.author.surname} {ba.author.name}" for ba in book.book_authors]
        genres = [bg.genre.name for bg in book.book_genres]
        quantity = book_locations.get(book.id, 0)
        books_data.append({
            "id": book.id,
            "title": book.title,
            "price": float(book.price),
            "in_stock": quantity > 0,
            "authors": ", ".join(authors) if authors else "Не указан",
            "genres": ", ".join(genres) if genres else "Не указан",
            "publisher": book.publisher.name if book.publisher else "Не указан",
            "description": book.description or "",
            "image_url": book.image_url if book.image_url else None,
            "quantity": quantity
        })
    return render_template('index.html', books=books_data, book_location=book_locations)

@app.route('/book_info/<int:book_id>')
def book_info(book_id):
    if 'employee_id' not in session:
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
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

@app.route('/shelf')
def shelf():
    if 'employee_id' not in session:
        flash("Пожалуйста, войдите в систему")
        return redirect(url_for('login'))
    return render_template('shelf.html')

@app.route('/publisher')
def show_publishers():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    publishers = Publisher.query.all()
    return render_template('publisher.html', publishers=publishers)

@app.route('/publisher/add', methods=['GET', 'POST'])
def add_publisher():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    if request.method == 'POST':
        new_name = request.form['name']
        if not new_name:
            flash("Название издательства не может быть пустым")
            return render_template('add_publisher.html')
        new_publisher = Publisher(name=new_name)
        db.session.add(new_publisher)
        db.session.commit()
        flash("Издательство успешно добавлено")
        return redirect(url_for('show_publishers'))
    return render_template('add_publisher.html')

@app.route('/publisher/edit/<int:publisher_id>', methods=['GET', 'POST'])
def edit_publisher(publisher_id):
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    publisher = Publisher.query.get_or_404(publisher_id)
    if request.method == 'POST':
        new_name = request.form['name']
        if not new_name:
            flash("Название издательства не может быть пустым")
            return render_template('edit_publisher.html', publisher=publisher)
        publisher.name = new_name
        db.session.commit()
        flash("Издательство успешно обновлено")
        return redirect(url_for('show_publishers'))
    return render_template('edit_publisher.html', publisher=publisher)

@app.route('/publisher/delete/<int:publisher_id>')
def delete_publisher(publisher_id):
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    publisher = Publisher.query.get_or_404(publisher_id)
    db.session.delete(publisher)
    db.session.commit()
    flash("Издательство успешно удалено")
    return redirect(url_for('show_publishers'))

@app.route('/genre')
def show_genres():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    genres = Genre.query.all()
    return render_template('genre.html', genres=genres)

@app.route('/theme')
def show_themes():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    themes = Theme.query.all()
    return render_template('theme.html', themes=themes)

@app.route('/author')
def show_authors():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    authors = Author.query.all()
    return render_template('author.html', authors=authors)

@app.route('/search_users', methods=['GET'])
def search_users():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    query = request.args.get('query', '')
    sql = text('''
        SELECT s."ID сотрудника", s."Фамилия" AS last_name, s."Имя" AS first_name, s."Отчество" AS middle_name,
               s."Телефон" AS phone, s."Почта" AS email, d."Название должности" AS position_name, s."Дата найма" AS hire_date
        FROM "Сотрудник" s JOIN "Должность" d ON s."ID должности" = d."ID должности"
        WHERE s."Фамилия" ILIKE :query OR s."Имя" ILIKE :query OR s."Почта" ILIKE :query
        ORDER BY s."ID сотрудника" LIMIT 50
    ''')
    result = db.session.execute(sql, {'query': f'%{query}%'})
    employees = [dict(row) for row in result.mappings()]
    return render_template('admin_main.html', employees=employees, search_query=query)

@app.route('/backup')
def backup():
    if 'employee_id' not in session or session.get('position') != 'Системный администратор':
        flash("У вас нет прав для доступа к этой странице")
        return redirect(url_for('show_books' if 'employee_id' in session else 'login'))
    flash("Функция резервного копирования пока не реализована")
    return redirect(url_for('show_employees'))



@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Пожалуйста, войдите в систему.'}), 401

    employee_id = session['employee_id']
    quantity = int(request.form.get('quantity', 1))

    book_location = BookLocation.query.filter_by(book_id=book_id).first()
    if not book_location:
        return jsonify({'success': False, 'error': 'Книга не найдена.'}), 400

    cart = Cart.query.filter_by(employee_id=employee_id, status='Активна').first()
    if not cart:
        if quantity > 0:
            cart = Cart(employee_id=employee_id)
            db.session.add(cart)
            db.session.commit()
        else:
            return jsonify({'success': True, 'quantity': 0, 'message': 'Корзина пуста.'})

    cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    if cart_item:
        if quantity <= 0:
            db.session.delete(cart_item)
            db.session.commit()
            if not CartItem.query.filter_by(cart_id=cart.id).first():
                db.session.delete(cart)
                db.session.commit()
            return jsonify({'success': True, 'quantity': 0, 'message': 'Товар удалён из корзины.'})
        elif quantity > book_location.quantity:
            return jsonify({'success': False, 'error': 'Недостаточно экземпляров в наличии.'}), 400
        else:
            cart_item.quantity = quantity
            db.session.commit()
            book = Book.query.get(book_id)
            return jsonify({'success': True, 'quantity': cart_item.quantity, 'message': f'Книга "{book.title}" обновлена в корзине.'})
    elif quantity > 0:
        if book_location.quantity >= quantity:
            cart_item = CartItem(cart_id=cart.id, book_id=book_id, quantity=quantity)
            db.session.add(cart_item)
            db.session.commit()
            book = Book.query.get(book_id)
            #return jsonify({'success': True, 'quantity': cart_item.quantity, 'message': f'Книга "{book.title}" добавлена в корзину.'})
        else:
            return jsonify({'success': False, 'error': 'Недостаточно экземпляров в наличии.'}), 400
    return jsonify({'success': True, 'quantity': 0, 'message': 'Нет изменений в корзине.'})
@app.route('/cart')
def cart():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        flash('Ваша корзина пуста.', 'info')
        return render_template('cart.html', items=[])
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    items = []
    total = 0
    for item in cart_items:
        book = Book.query.get(item.book_id)
        if book:
            subtotal = book.price * item.quantity
            total += subtotal
            items.append({
                'id': book.id,
                'title': book.title,
                'quantity': item.quantity,
                'price': float(book.price),
                'subtotal': float(subtotal),
                'image_url': url_for('static', filename=book.image_url) if book.image_url else None
            })
    return render_template('cart.html', items=items, total=total)

@app.route('/check_cart/<int:book_id>')
def check_cart(book_id):
    if 'employee_id' not in session:
        return jsonify({'quantity': 0})
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        return jsonify({'quantity': 0})
    cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    return jsonify({'quantity': cart_item.quantity if cart_item else 0})

@app.route('/remove_from_cart/<int:book_id>', methods=['POST'])
def remove_from_cart(book_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Пожалуйста, войдите в систему.'}), 401
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        return jsonify({'success': True, 'quantity': 0, 'message': 'Товар удалён из корзины.'})
    cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        if not CartItem.query.filter_by(cart_id=cart.id).first():
            db.session.delete(cart)
            db.session.commit()
        return jsonify({'success': True, 'quantity': 0, 'message': 'Товар удалён из корзины.'})
    return jsonify({'success': True, 'quantity': 0, 'message': 'Товар не найден в корзине.'})

@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        if 'employee_id' not in session:
            return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401

        data = request.get_json()
        payment_method = data.get('payment_method', 'cash')
        cart_id = data.get('cart_id')

        # Проверяем корзину
        cart = Cart.query.filter_by(id=cart_id, employee_id=session['employee_id'], status='Активна').first()
        if not cart:
            return jsonify({'success': False, 'error': 'Корзина не найдена'}), 400

        # Получаем все элементы корзины
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        if not cart_items:
            return jsonify({'success': False, 'error': 'Корзина пуста'}), 400

        # Обновляем остатки и удаляем книги
        for item in cart_items:
            book_location = BookLocation.query.filter_by(book_id=item.book_id).first()
            if book_location:
                if book_location.quantity < item.quantity:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': f'Недостаточно экземпляров книги ID {item.book_id}'}), 400
                book_location.quantity -= item.quantity
                if book_location.quantity == 0:
                    db.session.delete(book_location)  # Удаляем запись, если остаток стал 0

        # Очищаем корзину
        db.session.delete(cart)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Оплата прошла успешно'
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка в process_payment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/checkout')
def checkout():
    if 'employee_id' not in session:
        flash('Пожалуйста, войдите в систему.', 'error')
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        flash('Ваша корзина пуста.', 'info')
        return redirect(url_for('cart'))
    return redirect(url_for('checkout_pay'))

@app.route('/checkout_pay')
def checkout_pay():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        flash('Ваша корзина пуста.', 'info')
        return redirect(url_for('cart'))
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    total = sum(item.quantity * Book.query.get(item.book_id).price for item in cart_items)
    return render_template('checkout_pay.html', items=cart_items, total=float(total), cart_id=cart.id)

@app.route('/sale_success')
def sale_success():
    return render_template('sale_success.html')


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'employee_id' not in session:
        return jsonify({'error': 'Пожалуйста, войдите в систему.'}), 401

    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.delete(cart)
        db.session.commit()

    return jsonify({'success': True, 'message': 'Корзина очищена'})

@app.route('/update_cart/<int:book_id>', methods=['POST'])
def update_cart(book_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Пожалуйста, войдите в систему.'}), 401

    # Получаем запрошенное количество из формы
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        return jsonify({'error': 'Некорректное значение количества.'}), 400

    # Проверяем наличие книги
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Книга не найдена.'}), 404

    # Проверяем наличие на складе
    book_location = BookLocation.query.filter_by(book_id=book_id).first()
    if not book_location:
        return jsonify({'error': 'Книга отсутствует на складе.'}), 400

    # Проверяем корзину
    cart = Cart.query.filter_by(employee_id=session['employee_id'], status='Активна').first()
    if not cart:
        return jsonify({'error': 'Корзина не найдена.'}), 400

    # Проверяем элемент корзины
    cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    if not cart_item:
        return jsonify({'error': 'Книга не найдена в корзине.'}), 400

    # Проверяем новое количество
    if quantity <= 0:
        # Если количество <= 0, удаляем элемент из корзины
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({
            'success': True,
            'quantity': 0,
            'message': f'Книга "{book.title}" удалена из корзины.'
        })

    # Проверяем, достаточно ли книг на складе
    if book_location.quantity < quantity:
        return jsonify({'error': 'Недостаточно экземпляров в наличии.'}), 400

    # Обновляем количество
    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({
        'success': True,
        'quantity': cart_item.quantity,
        'price': float(book.price),
        'message': f'Количество книги "{book.title}" обновлено в корзине.'
    })
@app.route('/cart_count')
def cart_count():
    if 'employee_id' not in session:
        return jsonify({'success': True, 'count': 0})

    employee_id = session['employee_id']
    cart = Cart.query.filter_by(employee_id=employee_id, status='Активна').first()
    if not cart:
        return jsonify({'success': True, 'count': 0})

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    total_count = sum(item.quantity for item in cart_items) if cart_items else 0
    return jsonify({'success': True, 'count': total_count})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)