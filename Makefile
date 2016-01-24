import-wiki:
	python ./manage.py input from_fixture -f ../data/wiki.json -s WikiSource -m "naam=full_name&geboortedatum=birth_date"
	python ./manage.py extend add_to_master -s WikiSource

import-telephone:
	python ./manage.py input_source from_mysql_table -f white_subscriber -s PhoneBookSource -m "gemeente=district&lastname=last_name" 

import-nba:
	python ./manage.py input from_mysql_table -f nba -s NBASource -m "naam=name&voornaam=first_name&geboortedatum=birth_date&stad=city"

import-big:
	python ./manage.py input from_mysql_table -f big -s BIGSource -m "lastname=last_name&birthday=birth_date"

import-soccer:
	python ./manage.py input from_mysql_table -f voetballers -s SoccerSource -m "naam=full_name&datum=birth_date&profiel=profile" -d "%d/%m/%Y"
	python ./manage.py extend add_to_master -s SoccerSource

import-wie-o-wie:
	python ./manage.py input from_mysql_table -f wieowiepers -s WieOWieSource -m "name=full_name"
	python ./manage.py extend extend_master -s WieOWieSource

import-schoolbank:
	python ./manage.py input from_mysql_table -f schoolbank -s SchoolBankSource -m "naam=full_name&geboortejaar=birth_year&profielfoto=profile_picture&stad=city&scholen=schools"

import-acteursspot:
	python ./manage.py input from_records -f ../data/acteurs_spot.json -s ActeursSpotSource -m "achternaam=full_name&afbeelding=picture&voornaam=confirmed_first_name"

import-acteursspot:
	python ./manage.py input from_records -f ../data/benf_casting.json -s ActeursSpotSource -m "achternaam=full_name&afbeelding=picture&voornaam=confirmed_first_name"

