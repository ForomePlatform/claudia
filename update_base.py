import sys
from mongodb import connect
from mongodb import update
from start_annotate import start_annotate
from main_interpretator import all_datasets
from csv_to_json import csv_to_json

# This script update the data base.
# If key '-a' is absent then the upadate is fast
# (only for initial docs; not for genereated docs).
if __name__ == '__main__':
    mongo = connect()
    # Only initial docs
    update(mongo)
    if len(sys.argv) > 2 and sys.argv[2] == '-a':
        # snapshots
        all_datasets(mongo)
        # chunks
        start_annotate(mongo)
        # indexes of apriory diagnosed docs
        csv_to_json(mongo)
    print('Ok')
