import requests
import json
import sys
import os
import re
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_dated_images():
    print("Getting dated images")
    dated_images = []
    payload = {
        "length": 100
    }
    response = requests.post(base_url + "images/list",
                             auth = (nutanix_username, nutanix_password),
                             headers = headers,
                             verify = False,
                             data = json.dumps(payload))
    images = json.loads(response.text)
    # regex for matching the image name
    image_name_regex = re.compile("^Win2022_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$")
    # regex for searching the image's date within the name
    date_regex = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$")
    for image in images["entities"]:
        image_name = image["status"]["name"]
        if image_name_regex.match(image_name):
            date_search = date_regex.search(image_name)
            image_date_string = date_search.group(0)
            image_date = datetime.strptime(image_date_string, "%Y-%m-%d_%H-%M-%S")
            image_age = now - image_date
            dated_images.append({
                "name": image_name,
                "uuid": image["metadata"]["uuid"],
                "date": image_date,
                "age": image_age.days
            })
    print(dated_images)
    return dated_images

def get_image_data(image_uuid):
    print("Getting data for image {}".format(image_uuid))
    response = requests.get(base_url + "/images/" + image_uuid,
                            auth = (nutanix_username, nutanix_password),
                            verify=False)
    print(response.text)
    return json.loads(response.text)

def delete_image(image_uuid):
    print("Deleting image {}".format(image_uuid))
    response = requests.delete(base_url + "/images/" + image_uuid,
                               auth = (nutanix_username, nutanix_password),
                               headers = headers,
                               verify = False)
    output = json.loads(response.text)
    print(output)

if __name__ == '__main__':
    # Set varibles from args
    nutanix_url = sys.argv[1]
    nutanix_port = sys.argv[2]
    nutanix_username = sys.argv[3]
    nutanix_password = sys.argv[4]

    # Set variables from envs
    max_image_age_days = int(os.getenv("MAX_IMAGE_AGE_DAYS"))

    # Set variables for requests
    headers = {
        'Content-Type': "application/json"
    }
    base_url = "https://{}:{}/api/nutanix/v3/".format(nutanix_url, nutanix_port)

    now = datetime.now()

    for image in get_dated_images():
        if image["age"] >= max_image_age_days:
            print("Expired Image: {} - {}".format(image["uuid"], image["name"]))
            delete_image(image["uuid"])

    # Jazz Hands
    exit(0)
