# Contributing Guide

Thank you for contributing to Djask.


## Support questions

Please don't use the issue tracker for this. The issue tracker is a tool
to address bugs and feature requests in Djask itself. Use one of the
following resources for questions about using Djask or issues with your
own code:

- Search with Google first using: `site:stackoverflow.com Djask {search term, exception message, etc.}`.
- Ask on our [GitHub Discussion][_gh_discuss], create a discussion under
the "Q&A" category.
- Ask on [Stack Overflow][_so].

Include the following information in your post:

- Describe what you expected to happen.
- If possible, include a [minimal reproducible example][_mcve] to help us
identify the issue. This also helps check that the issue is not with
your own code.
- Describe what actually happened. Include the full traceback if there
was an exception.
- List your Python, Flask and Djask versions. If possible, check if this
issue is already fixed in the latest releases or the latest code in
the repository.

[_gh_discuss]: https://github.com/z-t-y/Djask/discussions
[_so]: https://stackoverflow.com/


## Reporting issues

If you find a bug related to Djask itself, or you think Djask
should provide a new feature/enhacement, feel free to create an
issue on our [issue tracker][_gh_issue].

Include the following information in your post:

- Describe what you expected to happen.
- If possible, include a [minimal reproducible example][_mcve] to help us
identify the issue. This also helps check that the issue is not with
your own code.
- Describe what actually happened. Include the full traceback if there
was an exception.
- List your Python, Flask and Djask versions. If possible, check if this
issue is already fixed in the latest releases or the latest code in
the repository.

[_gh_issue]: https://github.com/z-t-y/Djask/issues
[_mcve]: https://stackoverflow.com/help/minimal-reproducible-example


## Submitting patches

If there is not an open issue for what you want to submit, prefer
opening one for discussion before working on a PR. You can work on any
issue that doesn't have an open PR linked to it or a maintainer assigned
to it. These show up in the sidebar. No need to ask if you can work on
an issue that interests you.

Include the following in your patch:

- Include tests if your patch adds or changes code. Make sure the test
fails without your patch.
- Update any relevant docs pages and docstrings. Docs pages and
docstrings should be wrapped at 72 characters.
- Add an entry in `CHANGES.md`. Use the same style as other
entries. Also include `Version Changed` or `Version Added` section
in relevant docstrings.


### First time setup

- Download and install the latest version of Git.
- Configure git with your username and email.

```
$ git config --global user.name 'your name'
$ git config --global user.email 'your email'
```

- Make sure you have a GitHub account.
- Click the "[Fork][_fork]" button to fork Djask on GitHub.
- Clone your fork repository locally (replace `{username}` with your username):

```
$ git clone https://github.com/{username}/Djask
$ cd Djask
$ git remote add upstream https://github.com/z-t-y/Djask
```

- Create a virtual environment and install requirements:

For Linux/macOS:

```
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip setuptools
pip install -r requirements/dev.txt
pip install -e .
pre-commit install
```

For Windows:

```
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip setuptools
pip install -r .\requirements\dev.txt
pip install -e .
pre-commit install
```

[_fork]: https://github.com/z-t-y/Djask/fork


### Start coding

- Create a new branch to address the issue you want to work on (be sure to
update the example branch name):

```
$ git fetch upstream
$ git checkout -b your-branch-name upstream/main
```

- Using your favorite editor, make your changes,
[committing as you go][_commit]. Make sure the commit message follows [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/).
- Include tests that cover any code changes you make. Make sure the
test fails without your patch. Run the tests as described below.
- Push your commits to your fork on GitHub:

```
$ git push --set-upstream origin your-branch-name
```

- [Create a pull request][_pr]. Link to the issue being addressed with `fixes #123` in the pull request.

[_commit]: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
[_pr]: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request


### Running the tests

Run the basic test suite with pytest:

```
pytest
```

### Building the docs

```
cd docs
make html
python3 -m http.server -d=build/html
```

Open `localhost:8000` in your browser to view the docs.
