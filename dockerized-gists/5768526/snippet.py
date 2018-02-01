def json_response(view):
    @wraps(view)
    def decorator(*args, **kwargs):
        try:
            response = view(*args, **kwargs)
            return jsonify(response), 200
        except ValueError as valueError:
            return str(valueError), 400
        except LimitExceededError as limitExceeded:
            return str(limitExceeded), 429
        except Exception as exception:
            return str(exception), 500
    return decorator
