from flask import render_template, jsonify, request
from main import app


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/types")
def typesList():
    return render_template('types.html')
