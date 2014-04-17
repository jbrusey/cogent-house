#!/bin/sh

#nosetests
#pylint cogentviewer/models/ -f html > pylint.html 
pylint cogentviewer/views/ -f html > pylint.html 