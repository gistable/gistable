
import errno
import json
import os
import os.path

tf_state_path = os.path.join(os.path.dirname(__file__), "..", "terraform.tfstate")
tf_state_file = open(tf_state_path, 'rb')
tf_state = json.load(tf_state_file)
tf_state_file.close()

cert_output_path = os.path.join(os.path.dirname(__file__), "..", "certs")

root_resources = [mod["resources"] for mod in tf_state["modules"] if mod["path"] == ["root"]][0]

root_cert = root_resources["tls_self_signed_cert.root"]
root_cert_pem = root_cert["primary"]["attributes"]["cert_pem"]

issued_certs = {i: r for i, r in root_resources.iteritems() if r["type"] == "tls_locally_signed_cert"}

for resource_id, cert in issued_certs.iteritems():
    name = resource_id[len("tls_locally_signed_cert."):]
    attrs = cert["primary"]["attributes"]

    cert_pem = attrs["cert_pem"]

    cert_dir = os.path.join(cert_output_path, name)
    try:
        os.makedirs(cert_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

    cert_file = open(os.path.join(cert_dir, name + ".crt"), 'w')
    cert_file.write(cert_pem)
    cert_file.close()
    cert_file = open(os.path.join(cert_dir, "ca.crt"), 'w')
    cert_file.write(root_cert_pem)
    cert_file.close()
    cert_file = open(os.path.join(cert_dir, name + "-chained.crt"), 'w')
    cert_file.write(cert_pem)
    cert_file.write(root_cert_pem)
    cert_file.close()

    # If we also generated our own key for this certificate,
    # (as opposed to just being given a CSR from elsewhere)
    # then we'll write that out too, so we have all the
    # information needed to configure a server.
    if "tls_private_key." + name in root_resources:
        key_resource = root_resources["tls_private_key." + name]
        key_pem = key_resource["primary"]["attributes"]["private_key_pem"]
        cert_file = open(os.path.join(cert_dir, name + ".key"), 'w')
        cert_file.write(key_pem)
        cert_file.close()
