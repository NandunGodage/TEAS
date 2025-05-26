import boto3
from botocore.exceptions import NoCredentialsError


def upload_file_to_s3(file, bucket_name, object_name=None):
    """
    Upload a file to an S3 bucket and return the public URL.

    :param file: File-like object to upload
    :param bucket_name: Bucket to upload to
    :param object_name: S3 object name. If not specified, a default name is used
    :return: Public URL of the uploaded file, or None if upload failed
    """
    # If S3 object_name was not specified, use a default name
    if object_name is None:
        object_name = file.name  # Use the uploaded file's name as the object name

    # Create an S3 client
    s3_client = boto3.client('s3', 
                             region_name='ap-southeast-1',
                             aws_access_key_id='AKIAYTYM5KAGN2CJV46F',
                             aws_secret_access_key='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')

    try:
        # Upload the file
        s3_client.upload_fileobj(file, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})
        
        # Construct the public URL
        public_url = f"https://{bucket_name}.s3.ap-southeast-1.amazonaws.com/{object_name}"
        return public_url
    except FileNotFoundError:
        st.error("The file was not found")
        return None
    except NoCredentialsError:
        st.error("Credentials not available")
        return None
