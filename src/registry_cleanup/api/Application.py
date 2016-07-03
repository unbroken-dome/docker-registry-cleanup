import logging
import os
import sys

from flask import Flask

from ..model import Registry

app = Flask(__name__)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
app.logger.addHandler(stdout_handler)

registry_path = os.getenv('REGISTRY_PATH', '/var/lib/registry')
registry = Registry(registry_path)


# noinspection PyUnresolvedReferences
from . import RegistryApi, CleanupApi
