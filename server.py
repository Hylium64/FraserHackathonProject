from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Sample text content to be displayed during the session
texts = [
    "Welcome to the study session. Let's begin with Physics.",
    "Math is crucial for solving real-world problems.",
    "Biology is the study of life. What interests you the most?",
    "Chemistry helps us understand the composition of substances."
]

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle profile creation
@app.route('/create_profile', methods=['POST'])
def create_profile():
    data = request.json  # The profile data sent from frontend
    # Store or process the data as needed
    print(data)
    return jsonify({"message": "Profile created successfully!"})

# Route to handle starting a session
@app.route('/start_session', methods=['POST'])
def start_session():
    return jsonify({"text": random.choice(texts)})

if __name__ == '__main__':
    app.run(debug=True)
