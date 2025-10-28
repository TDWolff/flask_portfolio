import threading
import subprocess
# import "packages" from flask
from flask import render_template,request  # import render_template from "public" flask libraries
from flask.cli import AppGroup
from flask import Flask, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import dotenv
from flask_caching import Cache

from __init__ import app, cors  # Definitions initialization

pwss = os.getenv('redisp')

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '172.17.0.1',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_PASSWORD': pwss,
    'CACHE_DEFAULT_TIMEOUT': 300
})

dotenv.load_dotenv()

def get_key_for_limiter():
    """Custom key function that allows dev bypass"""
    # Check for dev authorization header
    dev_token = request.headers.get('X-Dev-Token')
    if dev_token and dev_token == os.getenv('DEV_TOKEN'):
        print(f"✅ Dev bypass granted for {get_remote_address()}")
        return None  # No rate limiting for authorized devs
    
    # Regular rate limiting for everyone else
    return get_remote_address()

def test_redis_connection():
    """Test if Redis is accessible before initializing limiter"""
    try:
        import redis        
        if pwss:
            r = redis.Redis(host='172.17.0.1', port=6379, password=pwss)
        else:
            r = redis.Redis(host='172.17.0.1', port=6379)
        r.ping()
        return True
    except Exception as e:
        print(f"Redis connection test failed: {e}")
        return False

# Create limiter instance with Redis storage
pwss = os.getenv('redisp')

# Test Redis connection first
if test_redis_connection():
    try:
        limiter = Limiter(
            key_func=get_key_for_limiter,  # Use custom key function
            default_limits=["200 per day", "30 per hour"],
            storage_uri=f"redis://:{pwss}@172.17.0.1:6379",
            storage_options={'socket_keepalive': True, 'socket_timeout': 5}
        )
        limiter.init_app(app)
        print("✅ Redis limiter initialized successfully")
    except Exception as e:
        print(f"❌ Redis limiter failed: {e}")
        # Fallback to memory
        limiter = Limiter(
            key_func=get_key_for_limiter,
            default_limits=["200 per day", "30 per hour"],
            storage_uri="memory://"
        )
        limiter.init_app(app)
        print("⚠️ Using memory storage as fallback")
else:
    # Use memory storage if Redis is not available
    limiter = Limiter(
        key_func=get_key_for_limiter,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    limiter.init_app(app)
    print("⚠️ Redis not available, using memory storage")
    
@app.route('/robots.txt')
def serve_robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')


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

@app.before_request
def log_suspicious_requests():
    # Log suspicious patterns
    user_agent = request.headers.get('User-Agent', '')
    if any(bot in user_agent.lower() for bot in ['sqlmap', 'nikto', 'nmap']):
        app.logger.warning(f"Suspicious user agent: {user_agent} from {request.remote_addr}")
    
    # Check for common attack patterns in URLs
    suspicious_patterns = ['../../../', 'script>', 'javascript:', 'data:']
    if any(pattern in request.url.lower() for pattern in suspicious_patterns):
        app.logger.warning(f"Suspicious URL pattern: {request.url} from {request.remote_addr}")

@app.route('/')  # connects default URL to index() function
@cache.cached(timeout=3600)
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

@app.route('/blender')
@cache.cached(timeout=3600)
def blender():
    return render_template("blender.html")

@app.route('/blogs')
def blogs():
    return render_template("blogs.html")

@app.route('/tutorials')
def tutorials():
    return render_template("tutorials.html")

@app.route('/table/')  # connects /stub/ URL to stub() function
@cache.cached(timeout=3600)
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
