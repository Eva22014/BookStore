from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

app = Flask(__name__)
password = "13060109"
encoded_password = quote_plus(password)

# Настройка подключения к PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{encoded_password}@localhost:5432/bookstore'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 5,
    'max_overflow': 2,
    'pool_recycle': 300
}

db = SQLAlchemy(app)

# Модель для таблицы Издательство
class Publisher(db.Model):
    __tablename__ = 'Издательство'
    id = db.Column('ID издательства', db.Integer, primary_key=True)
    name = db.Column('Название издательства', db.String(100), nullable=False, unique=True)

# Модель для таблицы Тематика
class Theme(db.Model):
    __tablename__ = 'Тематика'
    id = db.Column('ID тематики', db.Integer, primary_key=True)
    name = db.Column('Название тематики', db.String(100), nullable=False, unique=True)

# Модель для таблицы Автор
class Author(db.Model):
    __tablename__ = 'Автор'
    id = db.Column('ID автора', db.Integer, primary_key=True)
    surname = db.Column('Фамилия', db.String(100), nullable=False)
    name = db.Column('Имя', db.String(50), nullable=False)
    patronymic = db.Column('Отчество', db.String(50))

# Модель для таблицы Жанр
class Genre(db.Model):
    __tablename__ = 'Жанр'
    id = db.Column('ID жанра', db.Integer, primary_key=True)
    name = db.Column('Название жанра', db.String(100), nullable=False, unique=True)

# Модель для таблицы Книга
class Book(db.Model):
    __tablename__ = 'Книга'
    id = db.Column('ID книги', db.Integer, primary_key=True)
    title = db.Column('Название', db.String(255), nullable=False)
    year = db.Column('Год издания', db.Integer)
    price = db.Column('Цена', db.Numeric(10, 2), nullable=False)
    image_url = db.Column('Изображение', db.String(255))  # Поле для пути к изображению
    publisher_id = db.Column('ID издательства', db.Integer, db.ForeignKey('Издательство.ID издательства'))
    theme_id = db.Column('ID тематики', db.Integer, db.ForeignKey('Тематика.ID тематики'))
    description = db.Column('Описание', db.Text)  # Добавлено поле для описания

    # Отношения
    publisher = db.relationship('Publisher', backref='books')
    theme = db.relationship('Theme', backref='books')
    book_authors = db.relationship('BookAuthor', backref='book', cascade='all, delete-orphan')
    book_genres = db.relationship('BookGenre', backref='book', cascade='all, delete-orphan')

# Модель для таблицы Местоположение книги (для количества экземпляров)
class BookLocation(db.Model):
    __tablename__ = 'Местоположение книги'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    location_id = db.Column('ID места', db.Integer, db.ForeignKey('Место хранения.ID места'), primary_key=True)
    quantity = db.Column('Количество экземпляров', db.Integer, nullable=False)

    location = db.relationship('Location', backref='book_locations')

# Модель для таблицы Место хранения
class Location(db.Model):
    __tablename__ = 'Место хранения'
    id = db.Column('ID места', db.Integer, primary_key=True)
    name = db.Column('Название', db.String(100), nullable=False, unique=True)
    capacity = db.Column('Вместимость', db.Integer, nullable=False)
    location = db.Column('Местоположение', db.String(150), nullable=False)
    location_type_id = db.Column('ID типа места хранения', db.Integer, db.ForeignKey('Тип места хранения.ID места хранения'))

# Модель для таблицы Книга_Автор
class BookAuthor(db.Model):
    __tablename__ = 'Книга_Автор'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    author_id = db.Column('ID автора', db.Integer, db.ForeignKey('Автор.ID автора'), primary_key=True)

    author = db.relationship('Author', backref='book_authors')

# Модель для таблицы Книга_Жанр
class BookGenre(db.Model):
    __tablename__ = 'Книга_Жанр'
    book_id = db.Column('ID книги', db.Integer, db.ForeignKey('Книга.ID книги'), primary_key=True)
    genre_id = db.Column('ID жанра', db.Integer, db.ForeignKey('Жанр.ID жанра'), primary_key=True)

    genre = db.relationship('Genre', backref='book_genres')

@app.route('/')
def index():
    books = Book.query.all()
    books_data = []
    for book in books:
        # Получаем авторов
        authors = [f"{a.author.surname} {a.author.name} {a.author.patronymic or ''}".strip() for a in book.book_authors if a.author]
        # Получаем жанры
        genres = [g.genre.name for g in book.book_genres if g.genre]
        # Получаем количество экземпляров (если есть запись в Местоположение книги)
        quantity = BookLocation.query.filter_by(book_id=book.id).first().quantity if BookLocation.query.filter_by(book_id=book.id).first() else 0

        books_data.append({
            "id": book.id,
            "title": book.title,
            "price": float(book.price),
            "in_stock": quantity > 0,
            "image_url": book.image_url if book.image_url and book.image_url.startswith('images/') else None
        })
    return render_template('index.html', books=books_data)

@app.route('/book_info/<int:book_id>')
def book_info(book_id):
    book = Book.query.get_or_404(book_id)
    # Получаем авторов
    authors = [f"{a.author.surname} {a.author.name} {a.author.patronymic or ''}".strip() for a in book.book_authors if a.author]
    # Получаем жанры
    genres = [g.genre.name for g in book.book_genres if g.genre]
    # Получаем количество экземпляров
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
    return render_template('shelf.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создает только новые таблицы, если они не существуют
    app.run(debug=True, port=5001)

# Тестовое изменение для проверки Git, 08.06.2025ь