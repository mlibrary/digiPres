# babyblue

*** More complete documentation coming soon...

Based on https://django-globus-portal-framework.readthedocs.io/en/latest/

with info from: https://www.docker.com/blog/how-to-dockerize-django-app/

Adjust dockerfile and compose.yml
create wsgi.py file and .env file

----------------------

Related code here: https://github.com/mlibrary/digiPres/tree/main/containers/babyblue

To run this, pull the linked Docker image https://github.com/mutanthumb/baby-blue/pkgs/container/baby-blue:

Compostest.yml run the "noenv" image

docker compose -f compostest.yml up

This resolves authentication errors (PostgreSQL database is missing the core Django authentication tables)

docker compose exec web python manage.py migrate 



