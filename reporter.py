"""Report job statistics and graphs to webpage."""

import sys
import argparse

from autocms.core import load_configuration
from autocms.web import perform_test_reporting

def main():
    """Call perform_test_reporting with command line arguments."""
    parser = argparse.ArgumentParser(description='Submit one or more jobs.')
    parser.add_argument('testname', help='test directory')
    parser.add_argument('-c', '--configfile', type=str,
                        default='autocms.cfg',
                        help='AutoCMS configuration file name')
    args = parser.parse_args()
    config = load_configuration(args.configfile)
    perform_test_reporting(args.testname, config)
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
