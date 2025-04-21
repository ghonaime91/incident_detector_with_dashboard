from app import app
from flask import request, jsonify, render_template

# Errors Handlers
@app.errorhandler(400)
def bad_request(error):
    if (request.accept_mimetypes.accept_json and 
        not request.accept_mimetypes.accept_html):
        return jsonify({
            "success": False,
            "error": "Bad Request – Please check the request data and try again."
        }), 400
    else:
        return render_template("errors/400.html", error=error), 400


@app.errorhandler(404)
def not_found(error):
    if (request.accept_mimetypes.accept_json and 
        not request.accept_mimetypes.accept_html):
        return jsonify({
            "success": False,
            "error": "Not Found – The requested resource could not be found."
        }), 404
    else:
        return render_template("errors/404.html", error=error), 404


@app.errorhandler(405)
def method_not_allowed(error):
    if (request.accept_mimetypes.accept_json and 
        not request.accept_mimetypes.accept_html):
        return jsonify({
            "success": False,
            "error": "Method Not Allowed"
        }), 405
    else:
        return render_template("errors/405.html", error=error), 405


@app.errorhandler(500)
def internal_error(error):
    if (request.accept_mimetypes.accept_json and 
        not request.accept_mimetypes.accept_html):
        return jsonify({
            "success": False,
            "error": "Internal Server Error – Something went wrong on the server."
        }), 500
    else:
        return render_template("errors/500.html", error=error), 500