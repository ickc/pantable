# Pasteurize for Python 2

Pasteurize is used to backport form the Python3 code, such that the main code can be as clean as possible. Only in the cases that pasteurize fail to handle, an if-statement on `py2` is used to branch it between the 2 versions.

The procedure to pasteurize is in the `.travis.yml`. For example (always refer to `.travis.yml` in case this is not up-to-date),

```bash
mv setup.py setup.py.temp
mv pantable/version.py pantable/version.py.temp
pasteurize -wnj 4 .
mv setup.py.temp setup.py
mv pantable/version.py.temp pantable/version.py
```

(This is a dump way to pasteurize all python scripts except the `setup.py` or `version.py`.)

## Workflow Using Git

Now, the problem with testing your code in pasteurize is that you need to pasteurize and see if it passes the test. If it passes, you need to commit the code *without* the pasteurization however.

One possible way to do this, is before you pasteurize,

1. in git you stage all changes
2. pasteurize (now you code has unstaged files)
3. discard the unstaged changes

If you don't know how to stage your changes, then you might create a commit in step (1). Note that in this case if the test fails, you need to edit your previous commits, or create a new commits and squash it later.

If you don't know how to squash, then still feel free to create a pull request, but I'll squash all your commits into 1 when merged.

# Tests

Please include tests in pull requests. There's 2 kinds of tests here, one is Python unit test that calls the functions and compare the results. Another is to run pandoc directly and see if the output native AST is the same as a predefined one (usually generated automatically and just eyeballing to verify it's doing what it's supposed to do).

And also note that pep8 compliant is checked. Try `make test` to verify everything's right. Alternatively, you can activate Travis CI in your folk. Travis CI is setup to check these automatically. GitHub is set up to approve only if Travis CI is passed.
