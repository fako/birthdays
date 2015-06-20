import-wiki:
	python ./manage.py input from_fixture -f ../data/wiki.json -s WikiSource -m "naam=full_name&geboortedatum=birth_date" -a

import-telephone:
	python ./manage.py input from_mysql_table -f telefoonBoekGemeente -s PhoneBookSource -m "gemeente=district&lastname=last_name" 

import-nba:
	python ./manage.py input from_mysql_table -f nba -s NBASource -m "naam=name&voornaam=first_name&geboortedatum=birth_date&stad=city"

import-big:
	python ./manage.py input from_mysql_table -f big -s BIGSource -m "lastname=last_name&birthday=birth_date"

import-soccer:
	python ./manage.py input from_mysql_table -f voetballers -s SoccerSource -m "naam=full_name&datum=birth_date&profiel=profile" -d "%d/%m/%Y"

import-wie-o-wie:
	python ./manage.py input from_mysql_table -f wieowiepers -s WieOWieSource -m "name=full_name"

