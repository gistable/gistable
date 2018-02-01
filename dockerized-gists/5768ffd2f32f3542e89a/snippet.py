import boto3
import argparse

def main():
	argparser = argparse.ArgumentParser(description='Testing ARN stuff')
	argparser.add_argument("--role", help="If running with a role provide it here", required=True)
	argparser.add_argument("--profile", help="Credential profile", required=True)
	argparser.add_argument('--region', help='AWS Region to work within, defaults to eu-central-1', default='eu-central-1', required=False)
	args = argparser.parse_args()
	role = args.role
	profile = args.profile
	region = args.region

	session = boto3.session.Session(profile_name=profile, region_name=region)
	sts = session.client('sts')
	assumedRole = sts.assume_role(
				RoleArn=role,
				RoleSessionName='TestSession')

	boto3.setup_default_session(aws_access_key_id=assumedRole['Credentials']['AccessKeyId'], aws_secret_access_key=assumedRole['Credentials']['SecretAccessKey'], aws_session_token=assumedRole['Credentials']['SessionToken'], region_name=region)
	iamClient = boto3.client('iam')
	userlist = iamClient.list_users(MaxItems=1)
	print userlist['Users']
	if userlist['Users'][0]:
		accountId = userlist['Users'][0]['Arn'].split(':')[4]
		print('Account ID from the first IAM user')
		print(accountId)
	else:
		accountId = assumedRole['AssumedRoleUser']['Arn'].split(':')[4]
		print('Account ID from the Assumed Role')
		print(accountId)

main()