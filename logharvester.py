"""Collect information from and manage job log files."""

import sys
import argparse

from autocms.core import load_configuration
from autocms.harvest import perform_test_harvesting


def main():
    """Call perform_test_harvesting with command line arguments."""
    parser = argparse.ArgumentParser(description='Submit one or more jobs.')
    parser.add_argument('testname', help='test directory')
    parser.add_argument('-c', '--configfile', type=str,
                        default='autocms.cfg',
                        help='AutoCMS configuration file name')
    args = parser.parse_args()
    config = load_configuration(args.configfile)
    perform_test_harvesting(args.testname, config)
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
