from compose.cli.command import get_project
from maestro import app
import getopt
import logging
import os
import schedule
import sys
import threading
import time

import catalog
import groups
import persons
import services

cancel = False


log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)

root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

try:
    opts, args = getopt.getopt(sys.argv[1:], "hr", ["restart"])
except getopt.GetoptError:
    print('main.py -r')
    sys.exit(2)

logging.getLogger("schedule").propagate = False

log.info("Starting Maestro")

def update():
    schedule.every(1).minutes.do(services.update)
    while not cancel:
        schedule.run_pending()
        time.sleep(1)

workdir = os.getcwd()

log.info("Load catalog")

c = catalog.load(workdir)

log.info("Load services")

services.load(workdir)

for opt, arg in opts:
    if opt == '-h':
        print('main.py -r')
        sys.exit()
    elif opt in ("-r", "--restart"):
        services.restart('maestro-python')
        sys.exit()

threading.Thread(target=update).start()

log.info("Start server")

app.run(host='0.0.0.0', debug=True)

cancel = True

log.info("Exit...")
