# Customizing AutoCMS Reporting

The web page reporting on an AutoCMS test can be customized to meet the
needs of each test, report additional information about the jobs, 
and produce additional plots. A rudimentary knowledge of python 
is required to customize a test.

By default, the AutoCMS reporter builds a webpage by calling the 
`produce_default_webpage` function in the 
[autocms.web](../autocms/web.py) module. However, for a given test called
`some_test`, if there exists a module
`$AUTOCMS_BASEDIR/autocms/custom/some_test.py` and in that module there 
is a `produce_webpage` function, this customized function will 
be called instead of the default.

The `example_test` provides an 
[example custom module](../autocms/custom/example_test.py) where a 
specialized web page is created using the `produce_webpage` function 
in this module.

For the example test, an additional [token](tokens.md) is added to 
`autocms.cfg` called AUTOCMS_dice_sum_TOKEN is added which records the 
sum of two simulated dice rolled by the example test script. This 
enables reporting using the `dice_sum` attribute of every JobRecord
where the token was found in the output. The specialized webpage adds
this information to the report listing of failed jobs over the last 
24 hours:

```python
    webpage.add_failed_job_listing(24, dice_sum='Sum of the dice')
```

If there are successful jobs over the last 24 hours, it also produces
a histogram of the `dice_sum` attribute for all of the jobs:

```python
    if len(recent_successes) > 1:
        create_histogram('dice_sum', recent_successes, 'Sum of the Dice',
                         (5, 3), dice_plot_path)
        webpage.add_floating_image(30, 'dice.png',
                                   'Dice Rolls (last 24 hours):')
```

The `example_test` script and custom module is intended to be used as 
a template for creating other customized tests.
