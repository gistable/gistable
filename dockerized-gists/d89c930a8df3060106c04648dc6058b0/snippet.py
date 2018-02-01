def get_credential_service_account():
    from oauth2client.service_account import ServiceAccountCredentials
    SERVICE_ACC_CREDENTIAL = 'your-service-account-secrets-file.json'    
    scopes = ['https://www.googleapis.com/auth/drive']
    pprint("Request for credential received");
    
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACC_CREDENTIAL, scopes=scopes)
        pprint(credentials)
        return credentials
    except Exception as e:
        pprint("Failed to obtain valid credential")
        raise