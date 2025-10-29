from flask import Flask, render_template
from dashboard.dash_app import init_dashboard

app = Flask(__name__)

# Initialize the Dash dashboard inside Flask
init_dashboard(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
