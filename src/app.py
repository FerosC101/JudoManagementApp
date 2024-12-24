from flask import Flask
from config import DB_CONFIG


# template only hehe

app = Flask(__name__)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_CONFIG['vince']}:{DB_CONFIG['426999']}"
    f"@{DB_CONFIG['localhost']}:{DB_CONFIG['5432']}/{DB_CONFIG['judo_management']}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

app.register_blueprint(login.bp, url_prefix="/auth")
app.register_blueprint(register.bp, url_prefix="/auth")
app.register_blueprint(athletes.bp, url_prefix="/athletes")
app.register_blueprint(training.bp, url_prefix="/training")
app.register_blueprint(competitions.bp, url_prefix="/competitions")
app.register_blueprint(payments.bp, url_prefix="/payments")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
