import certstream

keywords = ['paypal', 'paypol']

def extract_domains(domains):
    res = []
    for domain in domains:
        for keyword in keywords:
            if keyword in domain:
                res.append(domain)
    return res

def print_callback(message, context):
    domains = message['data']['leaf_cert']['all_domains']
    res = extract_domains(domains)
    if len(res) > 0:
        print(res)

def on_open(instance):
    # Instance is the CertStreamClient instance that was opened
    print("Connection successfully established!")

def on_error(instance, exception):
    # Instance is the CertStreamClient instance that barfed
    print("Exception in CertStreamClient! -> {}".format(exception))

certstream.listen_for_events(print_callback, on_open=on_open, on_error=on_error)