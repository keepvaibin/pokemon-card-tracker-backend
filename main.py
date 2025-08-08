from flask import Flask
from app.routes import routes_bp  # import your blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(debug=True)
