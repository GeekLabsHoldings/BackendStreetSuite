import boto3
from django.conf import settings

def generate_presigned_url(file_name, file_type):
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': f'Media/{file_name}',  # Adjust the path as needed
                'ContentType': file_type
            },
            ExpiresIn=int(settings.AWS_PRESIGNED_EXPIRY.total_seconds())
        )
    except Exception as e:
        return None
    return response

def generate_presigned_url_for_read(file_name):
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': f'Media/{file_name}'  # Adjust the path as needed
            },
            ExpiresIn=int(settings.AWS_PRESIGNED_EXPIRY.total_seconds())
        )
    except Exception as e:
        return None
    return response