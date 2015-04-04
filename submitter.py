"""Submit and register one or more test jobs."""

import sys
import os
import argparse

from autocms.core import load_configuration
from autocms.submit import perform_test_submission


def main():
    """Call run_submission with arguments from the command line."""
    parser = argparse.ArgumentParser(description='Submit one or more jobs.')
    parser.add_argument('testname', help='test directory')
    parser.add_argument('-n', '--num_jobs', type=int, default=1,
                        help='number of jobs to submit (max)')
    parser.add_argument('-c', '--configfile', type=str,
                        default='autocms.cfg',
                        help='AutoCMS configuration file name')
    args = parser.parse_args()
    config = load_configuration(args.configfile)
    perform_test_submission(args.num_jobs, args.testname, config)
    return 0

if __name__ == '__main__':
    exit_status = main()
    sys.exit(exit_status)
