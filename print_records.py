"""Print all records in the pickle for the specified test"""

import sys
import argparse

from autocms.core import (load_configuration, load_records)


def main():
    """Print all records corresponding to test given as an argument"""
    parser = argparse.ArgumentParser(description='Submit one or more jobs.')
    parser.add_argument('testname', help='test directory')
    parser.add_argument('-c', '--configfile', type=str,
                        default='autocms.cfg',
                        help='AutoCMS configuration file name')
    args = parser.parse_args()
    config = load_configuration(args.configfile)
    records = load_records(args.testname,config)
    for job in records:
        print str(job)+'\n'
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
