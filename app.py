from flask import Flask, render_template
import sys

# Try import dash-based dashboard; print actionable instructions if missing.
try:
    from dashboard.dash_app import init_dashboard
except ModuleNotFoundError as e:
    missing = getattr(e, "name", str(e))
    print(
        "\nERROR: A required Python package is missing when importing the dashboard."
        f"\nMissing module: {missing}"
        "\n\nQuick steps to fix:"
        "\n  1) Create and activate a virtual environment:"
        "\n       python3 -m venv .venv"
        "\n       source .venv/bin/activate   # (or .venv\\Scripts\\activate on Windows)"
        "\n  2) Install dependencies:"
        "\n       pip install -r requirements.txt"
        "\n  3) Run the app:"
        "\n       python app.py"
        "\n\nIf you already installed packages, ensure the virtualenv is activated before running.\n"
    )
    sys.exit(1)

app = Flask(__name__)

# Initialize the Dash dashboard inside Flask
init_dashboard(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
