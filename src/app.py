from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vince:426999@localhost/judo_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/test_db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Database connected successfully!"
    except Exception as e:
        return f"Database connection error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
