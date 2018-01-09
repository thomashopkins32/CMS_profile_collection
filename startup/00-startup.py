import nslsii
nslsii.configure_base(get_ipython().user_ns, 'cms')

# At the end of every run, verify that files were saved and
# print a confirmation message.
from bluesky.callbacks.broker import verify_files_saved
# RE.subscribe(post_run(verify_files_saved), 'stop')

from pyOlog.ophyd_tools import *

# Uncomment the following lines to turn on verbose messages for
# debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)

# Add a callback that prints scan IDs at the start of each scan.
# def print_scan_ids(name, start_doc):
#     print("Transient Scan ID: {0} @ {1}".format(start_doc['scan_id'],time.strftime("%Y/%m/%d %H:%M:%S")))
#     print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))
# 
# RE.subscribe(print_scan_ids, 'start')
