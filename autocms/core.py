"""Common functions and classes for AutoCMS components."""

import re
import os
import cPickle as pickle

class JobRecord(object):
    """Information about a specific AutoCMS test job.

    A JobRecord may store arbitrarily many properties about a completed job
    depending on how the test is configured, but these are not guaranteed to
    exist until the logs are parsed and only if the corresponding token
    exists in the output log (see README.md for details).

    The following properties are set during construction and should be 
    guaranteed to exist (with the specified type if listed):

    jobid : the slurm job id or 'FAIL' if submission failed
    submit_time (int): timestamp of submission time.
    submit_status (int): exit code of 'sbatch' submission.
    start_time (int): timestamp of when the job started running
                      or zero if the job is not yet completed.
    end_time (int): timestamp of when the job completed
                    or zero if the job is not yet completed.
    node: hostname of the worker node that runs the job or 'N/A'. 
    logfile: standard output of the job reported through slurm or 'N/A'.
    completed (boolean): completion status of the job.
    exit_code (int): exit code returned by the job script
    exit_string: string describing the reason for job failure.
    """

    def __init__(self, submit_time, jobid, submit_status, **kwargs):
        """Construct JobRecord object from job information.

        Minimally a job requires submit_time to be  a timestamp for the
        submission time, jobid to either be a slurm job id or the literal
        'FAIL' if submission failed, and submit_status to be the exit code
        of the sbatch submission command.

        Additional keyword arguments may be given and will be set as object 
        properties, but this is mainly for use with __repr__.
        """
        self.submit_time = int(submit_time)
        self.jobid = jobid
        self.submit_status = int(submit_status)
        if self.submit_status == 0:
            self.node = "N/A"
            self.start_time = 0
            self.end_time = 0
            self.exit_code = 255
            self.error_string = "Job did not report success."
            self.completed = False
            self.logfile = "N/A"
        else:
            self.node = "N/A"
            self.start_time = self.submit_time
            self.end_time = self.submit_time
            self.exit_code = submit_status
            self.error_string = ("ERROR in job submission code " +
                                 str(submit_status))
            self.completed = True
            self.logfile = "N/A"
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def run_time(self):
        """Return total wall clock running time in seconds."""
        return self.end_time - self.start_time

    def wait_time(self):
        """Return total wall clock queued time in seconds."""
        return self.start_time - self.submit_time

    def is_success(self):
        """Return boolean job success status."""
        if self.exit_code == 0:
            return True
        else:
            return False

    def parse_output(self, logfile_name, config):
        """Parse job information from specified log file."""
        tokens = [s for s in config.keys()
                  if re.match(r'AUTOCMS_.*_TOKEN', s)]
        self.logfile = logfile_name
        with open(logfile_name, 'r') as handle:
            log = handle.read().splitlines()
        for line in log:
            for tok in tokens:
                if(re.match(config[tok], line)):
                    t_name = tok.replace('AUTOCMS_', '').replace('_TOKEN', '')
                    t_val = line.replace(config[tok], '')
                    if t_name == 'SUCCESS':
                        self.exit_code = 0
                        self.error_string = ''
                    else:
                        setattr(self, t_name, t_val)
        # ensure that required attributes remain ints - oddball log could 
        # mess this up
        self.exit_code = int(self.exit_code)
        self.start_time = int(self.start_time)
        self.end_time = int(self.end_time)
        # odd log could result in zero for start, end times
        # set to reasonable values        
        if self.start_time == 0:
            self.start_time = self.submit_time
        if self.end_time == 0:
            self.end_time = self.start_time

    def __repr__(self):
        """Return expression string to construct identical object."""
        s = 'JobRecord({0}, {1}, {2}'.format(self.submit_time,
                                             self.jobid,
                                             self.submit_status)
        more_attrs = (attr for attr in dir(self) 
                      if not attr.startswith('__') and
                         not callable(getattr(self,attr)) and
                         not attr == 'submit_time' and
                         not attr == 'jobid' and
                         not attr == 'submit_status')
        for attr in more_attrs:
            s += ", {0}={1}".format(attr,repr(getattr(self,attr)))
        s += ')'
        return s

    def __str__(self):
        """Return readable string of JobRecord object attributes."""
        attr_list = (attr for attr in dir(self) 
                     if not attr.startswith('__') and
                        not callable(getattr(self,attr)))
        s = "JobRecord object"
        for attr in attr_list:
            s += "\n    {0}={1}".format(attr, repr(getattr(self, attr)))
        return s


def load_configuration(filename):
    """Return configuration dict from filename."""
    config = dict()
    with open(filename,'r') as handle:
        config_raw = handle.read().splitlines()
    for line in config_raw:
        if( re.match(r'export', line) ):
            key = line.split('=')[0]
            key = key.replace("export", "")
            key = key.strip()
            val = line.split('=')[1]
            val = val.strip()
            val = val.strip('"')
            config[key] = val
    return config


def load_records(filename):
    """Get the JobRecord dictionary from the pickle or make a new one."""
    if os.path.isfile(filename):
        records = pickle.load(open(filename, "rb"))
    else:
        records = dict()
    return records


def save_records(records, filename):
    """Write the JobRecord dictionary to a pickle."""
    pickle.dump(records, open(filename, "wb"))
