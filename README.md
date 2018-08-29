# Jupyter Notebook Tools
This is a set of tools that is designed to facilitate science in the context of Osmo Systems.
The code herein generally expects to be run in the context of a jupyter notebook. TODO (PR feedback plz): eventually it might be used elsewhere. is it OK to put it all here for now and potentially have to refactor/move it later?

## What lives here

Here's the basic heuristic for what should live in this library vs. in a notebook.

**Is this function reusable across many experiments/activities, both now and for the foreseeable future, and is it fairly Osmo-specific?**
yes = probably it should live here. no = probably not.

Examples of code that should live here:

* Generalized database access functions
* Basic plots that are useful for a wide variety of experiments
* Calibration routines
* Analysis functions

Examples of code that should probably *not* live here:

* "get the standard deviation of a set of node data". Use `my_dataframe['my_column'].std()` as [implemented in pandas](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.std.html) instead.
* "check temperature and time correlation of each color count for each node during an experiment". This is probably too use-case specific and will end up as unmaintained, "dead code".

## Using this library

To consume this library in your notebook, add this line to the top:

`!pip install https://github.com/osmosystems/python-jupyter-tools.git@[VERSION]`
Where [VERSION] is a version number.

TODO: instructions for installing editable for testing/development purposes. include autoreload magics

## Contributing

### High Bar

The "bar" for including code in this library is higher than that seen in our jupyter notebooks. This is because:
* Code in a library is more trusted, less transparent
* Code in this library will be reused more, and thus it is more important for it to be correct and even more important for it to be maintainable

### Code Style

This repo follows the Osmo [Code Style Manifesto](https://docs.google.com/document/d/1W1Ipug8IACL4PfZAq5bQKlmfcJGmHGKNH95_FwJcjaI).
TODO: move the Python section there from proposal to "done"

#### Documentation

Function documentation should be in the [Google Style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings).

### Unit Tests

Run tests with `python setup.py test`
Any function that has a significant logic component that can be tested, should be unit tested.

# TODO  (PR feedback plz)
before this library is "ready to go" (or possibly after, if we decide). CR folks, these are questions for you: should we do these now or later
* fill out database-access functions
* actually test if I can consume it (might need some kind of GitHub auth setup)
* implement unit test framework
* implement linting
* fire up CircleCI so that we can see if unit tests and linting are passing on pull requests
