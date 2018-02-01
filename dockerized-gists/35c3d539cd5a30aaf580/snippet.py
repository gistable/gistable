# this is how to highlight code for powerpoint: `pbpaste | highlight --syntax=py -O rtf | pbcopy`

# api_jsonify()
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from flask import Response
from json import JSONEncoder, dumps

class JsonApiEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal) or isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, 'api_dump'):
            return o.api_dump()
        return JSONEncoder.default(self, o)

def api_dumps(obj):
    encoder_config = dict(cls=JsonApiEncoder, sort_keys=True, 
               indent=4)
    return dumps(obj, **encoder_config)

# role_aware_api_jsonify()
class RoleAwareEncoder(JsonApiEncoder):

    def default(self, o):
        if isinstance(o, User):
            base = o.api_dump()
            base['_can_update'] = can_update_user(o)
            base['_can_send_funds'] = can_send_funds_to_user(o)
            return base
        else:
            return super().default(o)

def role_aware_dumps(obj):
    encoder_config = dict(cls=RoleAwareEncoder, sort_keys=True, 
                          indent=4)
    return json.dumps(obj, **encoder_config)


def role_aware_jsonify(obj):
    return Response(role_aware_dumps(obj), mimetype='application/json')


def api_jsonify(obj):
    return Response(api_dumps(obj), mimetype='application/json')
    
# validation
card_funding_event_schema = {
    "properties": {
        "user_uuid": St.uuid,
        "amount": St.dollar_value,
    },
    "required": ["user_uuid", "amount"],
}

@bp.route("/card_funding_events", methods=["POST"])
@validate(card_funding_event_schema)
def new_funding_event_for_user():
    user = get_user(key=validated['user_uuid'])

    fe = CardFundingEvent()
    fe.card = user.card
    fe.load_amount = Decimal(validated['amount'])

    db.session.add(fe)
    db.session.commit()

    return role_aware_jsonify(fe)


# how it works
validated = LocalProxy(lambda: g.validated)

def check_schema(schema):
    jsonschema.Draft4Validator.check_schema(schema)

def validate(schema):
    check_schema(schema)

    def get_errors(data):
        v = jsonschema.Draft4Validator(schema)
        return sorted(v.iter_errors(data), key=lambda e: e.path)

    def validate_payload(data):
        errors = get_errors(data)
        if len(errors) > 0:
            raise ValidationException(errors)
        return data

    def validate_decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            g.validated = validate_payload(request.json)
            return fn(*args, **kwargs)
        return wrapped
    return validate_decorator

