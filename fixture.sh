#!/bin/bash

./manage.py dumpdata --format=json --indent=2 produccion
./manage.py dumpdata --format=json --indent=2 planificacion

