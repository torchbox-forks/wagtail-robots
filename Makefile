test:
	@python testmanage.py test

run:
	@python testmanage.py runserver

user:
	@echo "Creating superuser - Username: test Password: test"
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('test', '', 'test')" | python testmanage.py shell

migrate:
	@python testmanage.py migrate

tox-63:
	tox -e python3.10-django4.2-wagtail6.3

tox-70:
	tox -e python3.12-django5.1-wagtail7.0

tox-71:
	tox -e python3.13-django5.2-wagtail7.1
