migrate:
	python manage.py makemigrations
	python manage.py migrate

flake:
	- clear && echo "Running flake8..." && flake8 . && echo "Tests finished."

clean:
	isort **/*.py
	black .
	@echo "Done cleaning up code."
