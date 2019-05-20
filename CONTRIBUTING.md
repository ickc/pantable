# Tests

Please include tests in pull requests. There's 2 kinds of tests here, one is Python unit test that calls the functions and compare the results. Another is to run pandoc directly and see if the output native AST is the same as a predefined one (usually generated automatically and just eyeballing to verify it's doing what it's supposed to do).

And also note that pep8 compliant is checked. Try `make test` to verify everything's right. Alternatively, you can activate Travis CI in your folk. Travis CI is setup to check these automatically. GitHub is set up to approve only if Travis CI is passed.
