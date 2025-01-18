from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/messages.html")
def messages():
    return render_template('messages.html')

app.run()
