from flask import Flask

# Initialize the Flask app
app = Flask(__name__)

# Define a basic route
@app.route('/')
def home():
    return "Hello, World!"

# Define a dynamic route
@app.route('/greet/<name>')
def greet(name):
    return f"Hello, {name.capitalize()}!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
