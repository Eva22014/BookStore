from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hI3DIvF0YsymTSB2@db.vqcizotnverfqmmozxjx.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
@app.route('/')
def index():
    return "Hello, Ksushka!"

if __name__ == '__main__':
    app.run(debug=True)