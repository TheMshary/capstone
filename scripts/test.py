#!/usr/bin/env python

import requests


from requests.auth import HTTPBasicAuth


url = "http://capstone-dev-clone.us-west-2.elasticbeanstalk.com/predefinedservice/"

username = "Mshary2"
password = "testpass"

# response = requests.post(url, auth=HTTPBasicAuth(username, password))

# querystring = {"foo":["bar","baz"]}

# payload = "{\"username\": \"Mshary2\", \"password\":\"testpass\"}"
headers = {
    'Authorization': "Token acb0ec833b05ba05e9264aa5c5d67c0c415dfb13",
    'accept': "application/json",
    'content-type': "application/json",
    'x-pretty-print': "2"
    }

response = requests.request("GET", url, headers=headers)

print("REQUEST: ", response)
print("TEXT: ", response.text)