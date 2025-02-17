#!/bin/env python3
""" gets the secret from vault to write $HOME/.docker/config.json file """

import os
import sys
import hvac
from jinja2 import Template

VAULT_ROLE_ID = os.environ['VAULT_ROLE_ID']
VAULT_SECRET_ID = os.environ['VAULT_SECRET_ID']
VAULT_URL = os.environ['VAULT_URL']
DOCKER_TOKEN_PATH = os.environ['DOCKER_TOKEN_PATH']
DOCKER_CONFIG = os.environ['HOME']+'/.docker/config.json'


client = hvac.Client(url=VAULT_URL)
client.auth_approle(VAULT_ROLE_ID, VAULT_SECRET_ID)

if client.is_authenticated():
    vault_response = client.read(DOCKER_TOKEN_PATH)
    TEMPLATE = """{
  "auths": {
    "https://index.docker.io/v1/": {
      "auth": "{{ DOCKER_TOKEN }}"
    }
  },
  "HttpHeaders": {
    "User-Agent": "Docker-Client/19.03.13 (linux)"
  }
}
"""
    tm = Template(TEMPLATE)
    CONFIG = tm.render(DOCKER_TOKEN=vault_response['data']['DOCKER_TOKEN'])
    try:
        os.mkdir(os.environ['HOME']+'/.docker')
    except FileExistsError:
        pass
    try:
        file = open(DOCKER_CONFIG, "w")
        file.write(CONFIG)
        file.close()
    except (IOError,FileNotFoundError):
        print('failed to write the config')
else:
    print('vault auth failed')
    sys.exit(1)
