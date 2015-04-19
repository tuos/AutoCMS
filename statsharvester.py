"""Report summary statistics to persistent log file."""

import sys
import argparse

from autocms.core import load_configuration
from autocms.stats import perform_stats_harvesting


def main():
    """Call perform_stats_harvesting with command line arguments."""
    parser = argparse.ArgumentParser(description='Harvest summary statistics.')
    parser.add_argument('testname', help='test directory')
    parser.add_argument('-c', '--configfile', type=str,
                        default='autocms.cfg',
                        help='AutoCMS configuration file name')
    args = parser.parse_args()
    config = load_configuration(args.configfile)
    perform_stats_harvesting(args.testname, config)
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
