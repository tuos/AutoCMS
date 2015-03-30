"""Print all records in the pickle for the specified test"""

import os
import sys

from autocms.core import (JobRecord, load_records)


def main():
    """Print all records corresponding to test given as an  argument"""
    os.chdir(sys.argv[1])
    records = load_records('records.pickle')
    for key in records:
        print str(records[key])+"\n"


if __name__ == '__main__':
    status = main()
    sys.exit(status)
