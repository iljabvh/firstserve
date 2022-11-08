firstserve
==========

In this project we extract ATP and WTA tennis match data from https://www.kaggle.com/datasets/hwaitt/tennis-20112019 (atp.csv and wta.csv) and use it to develop a statistical framework analyzing tennis data.
The dataset includes match results and performance metrics from matches between 2011 and 2019. We collect the players' performance metrics (e.g. first serve percentage, points won after first serve, etc.) to perform interesting statistical analyses,
like prediction of match outcomes or determining the important performance metrics to win matches.


In the current release, we have

* built the framework to extract arbitrary performance metrics from the above dataset
* created dictionaries that store match information and player information
* included a demo file (demo_data.py) to show the fundamentals and to showcase the datasets with matplotlib

In the next release, we will

* introduce methods to store and retrieve the data in the .json format
* perform regression analysis with several methods (starting slowly, with Decision Tree algorithms) to predict match outcomes and head-to-head comparisons.



Feel free to use it and let me know what you think.


Getting started: Installation
-----------------------------

!!! As always, consider installing in a virtual environment !!!

After cloning the directory, simply install the requirements execute the setup.py file:

.. code::
    $ pip install -r requirements.txt
    $ python3 setup.py install

After the installation, before running demo_data.py, you need to include the dataset from https://www.kaggle.com/datasets/hwaitt/tennis-20112019 for the script to work (atp.csv or wta.csv).

Requirements
------------

This package requires only pandas so far, but we will start using scikit-learn in the next release.

Quickstart without Installation
------------

You can also simply clone this repository and run demo_data.py to get a feel for what this package does. Of course, you would need to handle the requirements yourself.
You will still need a dataset from https://www.kaggle.com/datasets/hwaitt/tennis-20112019 for the script to work (atp.csv or wta.csv)

Data
----

So far, we have only used the datasets from https://www.kaggle.com/datasets/hwaitt/tennis-20112019 (atp.csv and wta.csv),
which is licensed as https://creativecommons.org/licenses/by-nc/4.0/.

After the development of the data infrastructure in future releases,
We will add compatibility to other datasets as well and will probably mine match data from web sources directly.
The long term goal is to build a framework for seamless integration into the model from various sources.

**Author**

Ilja von Hoessle


