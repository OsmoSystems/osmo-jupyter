# Jupyter Notebook Tools
This is a set of tools that is designed to facilitate science in the context of Osmo Systems.
The code herein generally expects to be run in the context of a jupyter notebook.

## What lives here

Here's the basic heuristic for what should live in this library vs. in a notebook. **yes to all** = probably it should live here. **no to any** = probably not.

* Is this function reusable across many experiments/activities?
* Will that still be true for the foreseeable future?
* Is it fairly Osmo-specific?


Examples of code that should live here:

* Generalized database access functions
* Basic plots that are useful for a wide variety of experiments
* Calibration routines
* Analysis functions

Examples of code that should probably *not* live here:

* "get the standard deviation of a set of node data". Use `my_dataframe['my_column'].std()` as [implemented in pandas](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.std.html) instead. Anything that is not Osmo-specific is probably already implemented in an existing library that we should use instead.
* "check temperature and time correlation of each color count for each node during an experiment". This is probably too use-case specific and will end up as unmaintained, "dead code".

## Using this library

1. Before you can consume the library, you'll need to [set up an SSH key with GitHub](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/). This lets your computer access the private Git repository and you may have already done this.

2. Add these lines near the top of your notebook:

`!pip install --quiet git+ssh://git@github.com/osmosystems/osmo-jupyter.git@[CHANGESET]`

`import osmo_jupyter`

Replace [CHANGESET] with a changeset ID. Grab the latest changeset ID by [visiting GitHub](https://github.com/OsmoSystems/osmo-jupyter/commits/master). Click the uppermost "📋" button to copy the ID of the latest commit.

**note:** This will be the exact library version that your notebook depends on.


3. Once you run the cell you created above, Jupyter will be able to tab-complete all of our public functions: type `osmo_jupyter.` and `<tab>`.


## Contributing

### Feature requests

The software team takes feature requests and pull requests! Just talk to one of us and/or file a JIRA ticket in the [Feature Requests epic](https://osmobot.atlassian.net/browse/SOFT-306). Extra points for example code and clear explanations of what you're trying to accomplish.

### High Bar

The "bar" for including code in this library is higher than that seen in our jupyter notebooks. This is because:
* Code in a library is more trusted, less transparent
* Code in this library will be reused more, and thus it is more important for it to be correct and even more important for it to be maintainable

### Code Style

This repo follows the Osmo [Code Style Manifesto](https://docs.google.com/document/d/1W1Ipug8IACL4PfZAq5bQKlmfcJGmHGKNH95_FwJcjaI) as applies to Python code.


### Installing for development

1. Check out the repository and switch to its directory
2. Install the package "editable" so that you can edit it and consume the edited version: `pip install --editable .`


### Running tests

1. `pip install -r test_requirements.txt`
 to watch file changes and auto-run tests during development, call `pytest-watch`
2. to run unit tests, run `pytest`
3. to run the linter, use `flake8`
