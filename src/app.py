from flask import Flask
from auth import login, register
from routes import athletes, training, competition, payments

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(login.bp)
app.register_blueprint(register.bp)
app.register_blueprint(athletes.bp)
app.register_blueprint(training.bp)
app.register_blueprint(competition.bp)
app.register_blueprint(payments.bp)

if __name__ == "__main__":
    app.run(debug=True)
