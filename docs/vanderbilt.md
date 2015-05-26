# Vanderbilt T2 Specific Instructions

AutoCMS contains the `skim_test` used to test both the internal CMSSW
setup and LStore system with realisitic skimming jobs that work 
similarly to the production jobs sent through the grid.

The following steps are required to set up the T2 Vanderbilt 
site test:

1. Clone or download AutoCMS into a directory to be used as your 
AutoCMS base directory.  

2. Copy the file `autocms.cfg.vandy` to `autocms.cfg`

3. Using the editor of your choice, edit `autocms.cfg` to change
the following variables:

    * `AUTOCMS_BASEDIR` should be the absolute path to the directory where you have cloned the repostory

    * `AUTOCMS_CONFIGFILE` should be the absolute path to the `autocms.cfg` file, including the file name itself

    * `AUTOCMS_WEBDIR` should be the absolute path to a web-accessible directory where AutoCMS will create subdirectories, and manage files within those subdirectories. Note that `/home/username/web` is accessible at `https://www.hep.vanderbilt.edu/~username`.
 
    * `AUTOCMS_UNAME` should be your system user name that you will submit jobs to the scheduler as

    * `AUTOCMS_GNAME` should be the group or account that you will use to submit jobs to the scheduler. To ensure that your jobs run in the special testing account, set this to `cms_stage2`. Contact the ACCRE administrators if you do not have access to this SLURM account but are in charge of running the test.

    * Uncomment the line `export X509_USER_CERT=/home/username/.globus/usercert.pem` and change `username` to your username, or otherwise set the location to your certificate.

    * change `AUTOCMS_TEST_SUBWAITS` to a value of 1 if this is the production AutoCMS, or ask the T2 Administrators how often they want the test to run.

    * change `AUTOCMS_STAT_INTERVAL` to 3 or ask the T2 Administrators what statistics reporting interval is preferred.

4. Run `./autocms.sh print` to produce the crontab listing needed to run the 
autocms test at regular intervals, harvest the output logs, and report to 
the web page.

5. Add the printed lines to your crontab, or if you do not have an 
active crontab, run `crontab autocms.crontab` to add the lines. Make sure
that you are logged into the gateway node that you want AutoCMS jobs
to be submitted from. The system is now running. Keep track of which gateway
node you are running AutoCMS from. You may want to ask the T2 Admins which 
gateway that they prefer you use.

6. Wait about 30 minutes for jobs to run and the webpage to be generated,
maybe get a cup of coffee?

7. Test results should be generated with the webpage available at 
`$AUTOCMS_WEBDIR/skim_test/index.html`
