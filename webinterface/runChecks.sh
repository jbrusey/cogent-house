#!/bin/sh
pylint cogentviewer/models/ -f html  > pylint.html
nosetests cogentviewer/tests/testModels