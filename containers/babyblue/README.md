# babyblue

This is an Open Shift container version of the Baby Blue search interface digital preservation packages. 

Based on https://django-globus-portal-framework.readthedocs.io/en/latest/

with info from: https://www.docker.com/blog/how-to-dockerize-django-app/

Adjust settings.py and create wsgi.py. For OpenShift see Dockerfile, deployment.yaml and postgresdeployment.yml

I also created a secrets environment file in Open Shift. 

----------------------

The container is here: https://github.com/mlibrary/digiPres/pkgs/container/digipres%2Fbaby-blue

Connect Baby Blue with Postgresql:

oc exec deployment/baby-blue -- \
  python manage.py migrate



