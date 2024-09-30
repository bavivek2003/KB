import requests
import json
import sys
import os
from time import sleep
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def get_image_data(image_uuid):
    print("Getting data for image {}".format(image_uuid))
    response = requests.get(base_url + "/images/" + image_uuid,
                            auth = (nutanix_username, nutanix_password),
                            verify=False)
    print(response.text)
    return json.loads(response.text)

def update_image_name(image_uuid, new_name):
    print("Updating name for image {} to {}".format(image_uuid, new_name))
    image_data = get_image_data(image_uuid)
    image_data.pop("status")
    image_data["spec"]["name"] = new_name
    image_data["metadata"]["name"] = new_name
    payload = image_data
    response = requests.put(base_url + "/images/" + image_uuid,
                            auth = (nutanix_username, nutanix_password),
                            headers = headers,
                            verify=False,
                            data=json.dumps(payload))
    print(response.text)

if __name__ == '__main__':
    # Set varibles from args
    nutanix_url = sys.argv[1]
    nutanix_port = sys.argv[2]
    nutanix_username = sys.argv[3]
    nutanix_password = sys.argv[4]
    image_name = sys.argv[5]

    # Set variables for requests
    headers = {
        'Content-Type': "application/json"
    }
    base_url = "https://{}:{}/api/nutanix/v3/".format(nutanix_url, nutanix_port)

    latest_name = "Win2022_latest"

    old_latest_uuid = get_image_uuid(latest_name)

    max_60_second_wait_retries = int(os.getenv("MAX_60_SECOND_WAIT_RETRIES"))
    retries = 0

    # Wait until the image state is complete. Or timeout
    while True:
        image_uuid = get_image_uuid(image_name)
        if not image_uuid == None:
            image_data = get_image_data(image_uuid)
            if image_data["status"]["state"] == "COMPLETE":
                break
        print("Image {} is not yet ready.\nWaiting 60 seconds to retry.".format(image_name))
        if retries > max_60_second_wait_retries:
            print("Max retries reached. Timing out")
            exit(1)
        else:
            retries += 1
            sleep(60)

    # If a latest image exists, cycle it out first.
    if not old_latest_uuid == None:
        image_data = get_image_data(old_latest_uuid)
        # The description holds the original TEMPLATE_NAME as used by packer
        update_image_name(old_latest_uuid, image_data["spec"]["description"])
    # Move the new "Win2022-_master" to "Win2022_latest"
    update_image_name(image_uuid, latest_name)

    # Jazz Hands
    exit(0)
