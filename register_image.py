import requests
import boto3
import sys
import os
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_presigned_url(aws_access_key_id, aws_secret_access_key, endpoint_url, bucket_name, file_name):
    print("Generating presigned url for {} in {}".format(file_name, bucket_name))
    session = boto3.session.Session()
    s3_client = session.client(service_name = "s3",
                               aws_access_key_id = aws_access_key_id,
                               aws_secret_access_key = aws_secret_access_key,
                               endpoint_url = endpoint_url)
    parameters = {
        "Bucket": bucket_name,
        "Key": file_name
    }
    presigned_url = s3_client.generate_presigned_url('get_object',
                                           Params = parameters,
                                           ExpiresIn = 600)
    print(presigned_url)
    return presigned_url

def get_image_uuid(image_name):
    print("Getting UUID for image {}".format(image_name))
    image_uuid = None
    payload = {
        "length": 100
    }
    response = requests.post(base_url + "images/list",
                             auth = (nutanix_username, nutanix_password),
                             headers = headers,
                             verify = False,
                             data = json.dumps(payload))
    images = json.loads(response.text)
    for image in images["entities"]:
        if image["status"]["name"] == image_name:
            image_uuid = image["metadata"]["uuid"]
    print(image_uuid)
    return image_uuid

def upload_image(image_name, file_name, source_url):
    print("Uploading {} as {}".format(file_name, image_name))
    payload = {
        "spec": {
            "name": image_name,
            "resources": {
                "image_type": "DISK_IMAGE",
                "source_uri": source_url,
                "source_options": {
                    "allow_insecure_connection": True
                }
            },
            "description": file_name
        },
        "api_version": "3.1.0",
        "metadata": {
            "kind": "image",
            "name": image_name,
            "use_categories_mapping": True,
            "categories_mapping": {"Tower": ["Windows"]},
            "categories": {"Tower": "Windows"},
        }
    }
    response = requests.post(base_url + "images",
                             auth=(nutanix_username, nutanix_password),
                             headers= headers,
                             verify=False,
                             data=json.dumps(payload))
    print(response.text)

def delete_image(image_uuid):
    print("Deleteing image {}".format(image_uuid))
    response = requests.delete(base_url + "images/" + image_uuid,
                               auth = (nutanix_username, nutanix_password),
                               headers = headers,
                               verify = False)
    print(response.text)

if __name__ == '__main__':
    # Set varibles from args
    nutanix_url = sys.argv[1]
    nutanix_port = sys.argv[2]
    nutanix_username = sys.argv[3]
    nutanix_password = sys.argv[4]
    # source file
    file_name = sys.argv[5]
    # destination image
    image_name = sys.argv[6]

    # Set variables from envs
    aws_access_key_id = os.getenv('BUILD_BUCKET_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('BUILD_BUCKET_SECRET_ACCESS_KEY')
    endpoint_url = os.getenv('BUILD_BUCKET_ENDPOINT')
    bucket_name = os.getenv('BUILD_BUCKET_NAME')

    # Set variables for requests
    headers = {
        'Content-Type': "application/json"
    }
    base_url = "https://{}:{}/api/nutanix/v3/".format(nutanix_url, nutanix_port)

    # Generate presigned url for source file
    source_url = get_presigned_url(aws_access_key_id, aws_secret_access_key, endpoint_url, bucket_name, file_name)

    # Check for pre-existing image
    image_uuid = get_image_uuid(image_name)

    # If the image already exists delete it before uploading.
    if not image_uuid == None:
        delete_image(image_uuid)
    upload_image(image_name, file_name, source_url)

    # Jazz Hands
    exit(0)
