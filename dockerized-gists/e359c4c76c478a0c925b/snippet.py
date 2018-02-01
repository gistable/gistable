def generate_invitation_code():
    choices = string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(choices) for _ in range(6))

def get_temp_password():
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(choices) for _ in range(8))

def generate_coupon_code():
    choices = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(choices) for _ in range(16))
