from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from boto3 import Session


def assumed_session(role_arn, session_name, session=None):
    """STS Role assume a boto3.Session                                                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                                                                       
    With automatic credential renewal.                                                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                                                                       
    Args:                                                                                                                                                                                                                                                                                                                                              
      role_arn: iam role arn to assume                                                                                                                                                                                                                                                                                                                 
      session_name: client session identifier                                                                                                                                                                                                                                                                                                          
      session: an optional extant session, note session is captured                                                                                                                                                                                                                                                                                    
               in a function closure for renewing the sts assumed role.                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                       
    Notes: We have to poke at botocore internals a few times                                                                                                                                                                                                                                                                                           
    """
    if session is None:
        session = Session()

    def refresh():
        credentials = session.client('sts').assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name)['Credentials']
        return dict(
            access_key=credentials['AccessKeyId'],
            secret_key=credentials['SecretAccessKey'],
            token=credentials['SessionToken'],
            # Silly that we basically stringify so it can be parsed again                                                                                                                                                                                                                                                                              
            expiry_time=credentials['Expiration'].isoformat())

    session_credentials = RefreshableCredentials.create_from_metadata(
        metadata=refresh(),
        refresh_using=refresh,
        method='sts-assume-role')

    # so dirty.. it hurts, no clean way to set this outside of the internals poke                                                                                                                                                                                                                                                                      
    s = get_session()
    s._credentials = session_credentials
    region = session._session.get_config_variable('region') or 'us-east-1'
    s.set_config_variable('region', region)
    return Session(botocore_session=s)

