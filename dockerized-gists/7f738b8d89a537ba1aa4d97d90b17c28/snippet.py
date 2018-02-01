def lambda_handler(event, context):
    import subprocess
    result = subprocess.call("curl -I http://foo.bar", shell=True)
    return result
    