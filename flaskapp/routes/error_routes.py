from flask import render_template
from werkzeug.exceptions import HTTPException

from flaskapp.routes import routes_module


@routes_module.app_errorhandler(400)
@routes_module.app_errorhandler(401)
@routes_module.app_errorhandler(403)
@routes_module.app_errorhandler(404)
@routes_module.app_errorhandler(405)
@routes_module.app_errorhandler(408)
@routes_module.app_errorhandler(500)
@routes_module.app_errorhandler(502)
def handle_http_error(error):
    if isinstance(error, HTTPException):
        return render_template(
            'error.html',
            error_code=error.code,
            message=code_message(error)
        ), error.code


# Error code-wise message
def code_message(error):
    error_messages = {
        400: "Bad request",
        401: "Authorisation required",
        403: "You are forbidden to access this resource",
        404: "The page you are looking for does not exist",
        405: "This method is not allowed",
        408: "The application is taking too long to process your request",
        500: "The server was unable to process your request"
    }
    res = error_messages.get(error.code) \
        or error.name + " : " + error.description \
        or "Something went wrong"
    return res
