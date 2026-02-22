from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS

from src.routes.summary import summary_bp
from src.routes.intake import intake_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(summary_bp, url_prefix="/api/summary")
app.register_blueprint(intake_bp, url_prefix="/api/intake")

if __name__ == "__main__":
    print("Summary service running on port 3000")
    app.run(host="0.0.0.0", port=3000)
