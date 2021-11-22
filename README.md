# AENTS

## Setup a new instance

1. clone the repository
1. `python manage.py migrate`
1. `python manage.py createsuperuser`
1. `python manage.py loaddata encounters/fixtures/animal_type.json`
1. `python manage.py loaddata encounters/fixtures/animal.json`

## Backup 
1. `python manage.py dumpdata > all_the_data.json`

## Restore
1. `python manage.py loaddata all_the_data.json`