from flask import jsonify
from ooiservices.app.main import api

class ValidationError(ValueError):
    pass

def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def internal_server_error(message):
    response = jsonify({'error': 'internal server error', 'message': message})
    response.status_code = 500
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])

