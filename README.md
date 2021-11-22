# AENTS

Charley Mays developed the **A**nimal **En**counter **T**racking **S**ystem to facilitate the Greensboro Science Center's management of their animal encounters.

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

## Acknowledgements
1. The Greensboro Science Center Staff...