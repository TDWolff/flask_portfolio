import threading
import subprocess
# import "packages" from flask
from flask import render_template,request  # import render_template from "public" flask libraries
from flask.cli import AppGroup
from flask import Flask, jsonify
import os


# import "packages" from "this" project
from __init__ import app, cors  # Definitions initialization

# from api.user import user_api # Blueprint import api definition

# # setup App pages
# from projects.projects import app_projects # Blueprint directory import projects definition

# # register URIs
# app.register_blueprint(user_api) # register api routes
# app.register_blueprint(app_projects) # register app pages

# @app.route('/api/movies', methods=['GET'])
# def get_movies():
#     movies = os.listdir('/movies')
#     return jsonify(movies)

@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/')  # connects default URL to index() function
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/resume')
def resume():
    return render_template("resume.html")

@app.route('/blogs')
def blogs():
    return render_template("blogs.html")

@app.route('/table/')  # connects /stub/ URL to stub() function
def table():
    return render_template("table.html")

@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:8086', 'http://127.0.0.1:8086', 'https://nighthawkcoders.github.io']:
        cors._origins = allowed_origin

# Create an AppGroup for custom commands
custom_cli = AppGroup('custom', help='Custom commands')

# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)
        
# this runs the application on the development server
if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port="8086")
