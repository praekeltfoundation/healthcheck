migrate:
	python manage.py makemigrations
	python manage.py migrate

flake:
	- clear && echo "Running flake8..." && flake8 .