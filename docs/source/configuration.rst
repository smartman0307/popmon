===============
Report settings
===============

Some more details on stability report settings, in particular how to set:
the reference dataset, binning specifications, monitoring rules, and where to plot boundaries.

Using ``Settings`` for configuration
------------------------------------

As of ``popmon`` v1.0.0, most options are specified on the ``Settings`` object, that is provided to the package.
Instantiating an object with the default settings and passing it to ``popmon`` is as simple as:

.. code-block:: python

    from popmon import Settings

    settings = Settings()
    df.pm_stability_report(settings=settings)

In the next example, we change the ``reference_type`` to ``"rolling"``:

.. code-block:: python

    from popmon import Settings

    settings = Settings()
    settings.reference_type = "rolling"

    df.pm_stability_report(settings=settings)

``reference_type`` is one of the options that is defined on the top level of ``Settings``.
Other parameters are logically grouped, such as the options related to the HTML report.
Changing grouped items works similarly:

.. code-block:: python

    from popmon import Settings

    settings = Settings()
    settings.report.title = "Report showing fewer stats"
    settings.report.extended_report = False
    settings.report.show_stats = ["distinct*", "filled*", "nan*"]

    df.pm_stability_report(settings=settings)


A full overview of settings is available in the :doc:`api documentation <popmon>` (or one could view the `config.py <https://github.com/ing-bank/popmon/blob/master/popmon/config.py>`_).
The settings management is created on top of `pydantic <https://github.com/samuelcolvin/pydantic>`_.
For detailed instructions on how the settings object can be used, for instance exporting, we refer to `their documentation <https://pydantic-docs.helpmanual.io/>`_.

The settings are validated on assignment, and when the validation fails an ``ValidationError`` will be raised.

In some examples you may encounter an alternative syntax that has the same effect.
For completeness, we list them below:

.. code-block:: python

    from popmon import Settings

    # consider providing settings in the following way
    settings = Settings()
    settings.time_axis = "date"
    df.pm_stability_report(settings=settings)

    # This is identical to passing the parameters directly to the settings object
    settings = Settings(time_axis="date")
    df.pm_stability_report(settings=settings)

    # When not passing the `settings` argument, keyword arguments will be passed on to a newly instantiated
    # Settings object. This allows us to even do:
    df.pm_stability_report(time_axis="date")


Binning specifications
----------------------

Without any specific binning specification provided, by default automatic binning is applied to numeric and timestamp
features. Binning specification is a dictionary used for specific rebinning of numeric or timestamp features.

To specify the time-axis binning alone, do:

.. code-block:: python

  report = df.pm_stability_report(
      time_axis="date", time_width="1w", time_offset="2020-1-6"
  )

The ``time_axis`` argument should be the name of a column that is of type **numeric (e.g. batch id, time in ns) or date(time)**.
The default time width is 30 days ('30d'), with time offset 2010-1-4 (a Monday).
All other features (except for 'date') are auto-binned in this example.

To specify your own binning specifications for individual features or combinations of features, do:

.. code-block:: python

  # generate stability report with specific binning specifications
  report = df.pm_stability_report(bin_specs=your_bin_specs)

An example bin_specs dictionary is:

.. code-block:: python

    bin_specs = {
        "x": {"bin_width": 1, "bin_offset": 0},
        "y": {"num": 10, "low": 0.0, "high": 2.0},
        "x:y": [{}, {"num": 5, "low": 0.0, "high": 1.0}],
        "date": {
            "bin_width": pd.Timedelta("4w").value,
            "bin_offset": pd.Timestamp("2015-1-1").value,
        },
    }

In the bin specs for 'x:y', 'x' is not provided (here) and reverts to the 1-dim setting.
Any time-axis, when specified here ('date'), needs to be specified in nanoseconds. This takes precedence over
the input arguments ``time_width`` and ``time_offset``.

The 'bin_width', 'bin_offset' notation makes an open-ended histogram (for that feature) with given bin width
and offset. 'bin_offset' is the lower edge of the bin with internal index 0.

The notation 'num', 'low', 'high' gives a fixed range histogram from 'low' to 'high' with 'num'
number of bins.


Monitoring rules
----------------

The monitoring rules are used to generate traffic light alerts.

As indicated we use traffic lights to indicate where large deviations from the reference occur.
By default we determine the traffic lights as set as follows:

* Green traffic light: the value of interest is less than four standard deviations away from the reference.
* Yellow traffic light: the value of interest is between four and seven standard deviations away from the reference.
* Red traffic light: the value of interest is more than seven standard deviations away from the reference.

When generating a report, they can be provided as a dictionary:

.. code-block:: python

  settings = Settings()
  settings.monitoring.monitoring_rules = your_monitoring_rules

  # generate stability report with specific monitoring rules
  report = df.pm_stability_report(settings=settings)

When not provided, the default setting is:

.. code-block:: python

    monitoring_rules = {
        "*_pull": [7, 4, -4, -7],
        "*_zscore": [7, 4, -4, -7],
        "[!p]*_unknown_labels": [0.5, 0.5, 0, 0],
    }

Note that the (filename based) wildcards such as * apply to all statistic names matching that pattern.
For example, ``"*_pull"`` applies for all features to all statistics ending on "_pull". Same for ``"*_zscore"``.
For ``"[!p]*_unknown_labels"``, the rule is not applied to any statistic starting with the letter p.

Each monitoring rule always has 4 numbers, e.g. by default for each pull: [7, 4, -4, -7].

* The inner two numbers of the list correspond to the high and low boundaries of the yellow traffic light,
  so +4 and -4 in this example.
* The outer two numbers of the list correspond to the high and low boundaries of the red traffic light,
  so +7 and -7 in this example.

You can also specify rules for specific features and/or statistics by leaving out wildcards and putting the
feature name in front. This also works for a combinations of two features. E.g.

.. code-block:: python

    monitoring_rules = {
        "featureA:*_pull": [5, 3, -3, -5],
        "featureA:featureB:*_pull": [6, 3, -3, -6],
        "featureA:nan": [4, 1, 0, 0],
        "*_pull": [7, 4, -4, -7],
        "nan": [8, 1, 0, 0],
    }

In the case where multiple rules could apply for a feature's statistic, the most specific one gets applied.
So in case of the statistic "nan": "featureA:nan" is used for "featureA", and the other "nan" rule
for all other features.


Plotting of traffic light boundaries
------------------------------------

Where the red and yellow boundaries are shown in a plot of a feature's statistic can be set with the
``pull_rules`` option. Usually the same numbers are used here as for the monitoring rules, but this is
not necessary.

Note that, depending on the chosen reference data set, the reference mean and standard deviation can change
over time. The red and yellow boundaries used to assign traffic lights can therefore change over
time as well.

When generating a report, the ``pull_rules`` can be provided as a dictionary:

.. code-block:: python

  settings = Settings()
  settings.monitoring.pull_rules = your_pull_rules

  # generate stability report with specific monitoring rules
  report = df.pm_stability_report(settings=settings)

The default for `pull_rules` is:

.. code-block:: python

    pull_rules = {"*_pull": [7, 4, -4, -7]}

This means that the shown yellow boundaries are at -4, +4 standard deviations around the (reference) mean,
and the shown red boundaries are at -7, +7 standard deviations around the (reference) mean.

Note that the (filename based) wildcards such as * apply to all statistic names matching that pattern.
The same wild card logic applies as for the monitoring rules.


Just metrics, no report
-----------------------

When you're only interested in generating the metrics for the report, but not actually generate the report,
you can do the following:

.. code-block:: python

  # generate stability metrics but no report
  datastore = df.pm_stability_metrics()

This function has the exact same options as discussed in the sections above.

The datastore is a dictionary that contains all evaluated metrics displayed in the report.
For example, you will see the keys ``profiles``, ``comparisons``, ``traffic_lights`` and ``alerts``.

Each of these objects is in itself a dictionary that has as keys the features in the corresponding report-section,
and every key points to a pandas dataframe with the metrics of that feature over time.

Spark usage
-----------

``popmon`` works with Apache Spark. The following example demonstrates how to use them together.

.. code-block:: python

    import popmon
    from pyspark.sql import SparkSession

    # downloads histogrammar jar files if not already installed, used for histogramming of spark dataframe
    spark = SparkSession.builder.config(
        "spark.jars.packages",
        "io.github.histogrammar:histogrammar_2.12:1.0.20,io.github.histogrammar:histogrammar-sparksql_2.12:1.0.20",
    ).getOrCreate()

    # load a dataframe
    spark_df = spark.read.format("csv").options(header="true").load("file.csv")

    # generate the report
    report = spark_df.pm_stability_report(time_axis="timestamp")


Spark example on Google Colab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This snippet contains the instructions for setting up a minimal environment for popmon on Google Colab as a reference.

.. code-block:: console

    !apt-get install openjdk-8-jdk-headless -qq > /dev/null
    !wget -q https://www-us.apache.org/dist/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz
    !tar xf spark-2.4.7-bin-hadoop2.7.tgz
    !wget -P /content/spark-2.4.7-bin-hadoop2.7/jars/ -q https://repo1.maven.org/maven2/io/github/histogrammar/histogrammar-sparksql_2.12/1.0.20/histogrammar-sparksql_2.12-1.0.20.jar
    !wget -P /content/spark-2.4.7-bin-hadoop2.7/jars/ -q https://repo1.maven.org/maven2/io/github/histogrammar/histogrammar_2.12/1.0.20/histogrammar_2.12-1.0.20.jar
    !pip install -q findspark popmon

Now that spark is installed, restart the runtime.

.. code-block:: python

  import os

  os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
  os.environ["SPARK_HOME"] = "/content/spark-2.4.7-bin-hadoop2.7"

  import findspark

  findspark.init()

  from pyspark.sql import SparkSession

  spark = (
      SparkSession.builder.master("local[*]")
      .config(
          "spark.jars",
          "/content/jars/histogrammar_2.12-1.0.20.jar,/content/jars/histogrammar-sparksql_2.12-1.0.20.jar",
      )
      .config("spark.sql.execution.arrow.enabled", "false")
      .config("spark.sql.session.timeZone", "GMT")
      .getOrCreate()
  )

Troubleshooting Spark
~~~~~~~~~~~~~~~~~~~~~

The following section documents error that you may run into using spark, and how they can be resolved.

    TypeError: 'JavaPackage' object is not callable 

This error occurs when pyspark cannot find the required jars. Ensure that the location of "spark.jars" or "spark.jars.packages" is correct (see examples above). Stop the spark session and restart it with the exact location. You can use the ones hosted on github using the "spark.jars.pacakges" example or place the jars locally and use "spark.jars", depending on whichever is easiest in your setup.

If you are running in a jupyter notebook, then the kernel needs to be restarted.

Global configuration
--------------------

A number of settings is configured globally.
These can be found in the ``popmon.config`` module.
At the moment of writing this covers parallel processing.

The following snippet modifies the number of jobs and the backend used by ``joblib.Parallel``:

.. code-block:: python

    import popmon
    import popmon.config

    # Set Parallel to use 4 threads
    popmon.config.parallel_args["n_jobs"] = 4
    popmon.config.parallel_args["backend"] = "threading"

    # Create report as usual
    report = df.pm_stability_report(reference_type="self")
