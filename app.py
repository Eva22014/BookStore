from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hI3D1vF9YsynTSB2@db.vqcizotnverfqmmozxjx.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для страницы с информацией о книге
@app.route('/book_info')
def book_info():
    return render_template('book_info.html')

# Маршрут для страницы стеллажей
@app.route('/shelf')
def shelf():
    return render_template('shelf.html')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)