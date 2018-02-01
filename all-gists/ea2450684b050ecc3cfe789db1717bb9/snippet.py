import boto3
import click

@click.command()
@click.argument("bucket")
@click.argument("key")
@click.option("-e", "--expiration", default=3600, type=int, help="How long this presigned URL will live for")
def presign_s3(bucket, key, expiration):
    """ Simple utility to generate presigned URL on S3 (Default 1 hour expiration)

    \b
    Common Usage:
    
        python presign_url.py myS3Bucket Key -e 28800
        python presign_url.py myS3Bucket Key
    """
    params = {
        'Bucket': bucket,
        'Key': key
    }
    s3 = boto3.client('s3')
    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=expiration)
    click.echo(url, nl=False)

if __name__ == '__main__':
    presign_s3()