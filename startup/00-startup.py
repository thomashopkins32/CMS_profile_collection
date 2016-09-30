# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

from metadatastore.mds import MDS
# from metadataclient.mds import MDS
from databroker import Broker
from databroker.core import register_builtin_handlers
from filestore.fs import FileStore

# pull from /etc/metadatastore/connection.yaml
mds = MDS({'host': 'xf11bm-ca1',
           'port': 27017,
           'database': 'metadatastore-production-v1',
           'timezone': 'US/Eastern'}, auth=False)
# mds = MDS({'host': CA, 'port': 7770})

# pull configuration from /etc/filestore/connection.yaml
db = Broker(mds, FileStore({'host': 'xf11bm-ca1',
           'port': 27017,
           'database': 'filestore-production-v1',
           'timezone': 'US/Eastern'}))
register_builtin_handlers(db.fs)

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
from bluesky.global_state import gs
gs.RE.subscribe('all', db.mds.insert)

# At the end of every run, verify that files were saved and
# print a confirmation message.
# from bluesky.callbacks.broker import verify_files_saved
# gs.RE.subscribe('stop', post_run(verify_files_saved))

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.global_state import gs, abort, stop, resume
#from databroker import (DataBroker as db, get_events, get_images,
#                        get_table, get_fields, restream, process)
from time import sleep
import numpy as np

RE = gs.RE  # convenience alias

# Uncomment the following lines to turn on verbose messages for debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)
