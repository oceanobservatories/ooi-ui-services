[![Build Status](https://travis-ci.org/oceanobservatories/ooi-ui-services.svg?branch=master)](https://travis-ci.org/oceanobservatories/ooi-ui-services)

ooi-ui-services
===============

Ocean Observatories Initiative - User Interface Services

## Services
The WSGI service endpoints are listed and defined below:
Active Routes for Listing:

    /arrays
    /get_data
    /organization
    /parameters
    /platform_deployments
        /platform_deployments?array_id=
    /instrument_deployments
        /instrument_deployments?platform_deployment_id=
    /streams
        /streams?instrument_id=
    /platformlocation
        /platformlocation?reference_designator=
    /display_name?reference_designator=

Active Routes for specific item deployment inspection:

    /arrays/<string:array_code>
    /parameters/<string:id>
    /platform_deployments/<string:reference_designator>
    /instrument_deployments/<string:reference_designator>
    /streams/<string:stream_name>
    /parameter/<string:stream_parameter_name>

POST routes:

    /annotation
        'comment':
        'field_x':
        'field_y':
        'y-files':
        'instrument_name':
        'pos_x':
        'pos_y':
        'stream_name':
        'title': 'test'
        'user_name':

uFrame normalized routes:

    /get_data/<instrument>/<sensor>

### Configuration
Be sure to edit your `ooiservices/app/config.yml` file to the correct URLs and Database Connectors.

### Service setup
Ensure you have the following:

    sudo apt-get update -qq
    sudo apt-get install -y python-dev
    sudo apt-get install -y python-matplotlib
    sudo apt-get install -y libhdf5-serial-dev
    sudo apt-get install -y libnetcdf-dev
      
While in your virtualenv, run the requirement.txt file:
    pip install -r ooiservuces/requirements/dev.txt

Setup your PostgreSQL environment:
    install postgis...

Make sure you have the environment variables defiend:

    PYTHONPATH=.
    
### Setup the Database:

```
python ooiservices/manage.py deploy --password <admin-password> --psqluser <postgres authorized user --production
```

    --password is required
    --psqluser is optional, default is postgres
    --production will create the ooiuiprod database instead of ooiuidev and ooiuitest

    Note: Only works on *nix systems.  Windows users must create the desired database manually
    and use rebuild_schema to deploy
    
    Note: On all systems, rebuild_schema rebuilds the target schema within the active database connection 
    (in config.yml or config_local.yml) with the option to save the existing users, 
    add more admin user information, choose the target schema and schema owner.


### Debugging Database Problems

If you attempt to deploy the database `ooiservices/manage.py deploy` and
encounter an error "role postgres does not exist". You need to create the role
postgres. You can do so by

```
psql postgres
CREATE ROLE postgres LOGIN SUPERUSER;
```

### Run Redis

Ensure redis-server is installed, running and that the python env works

```
python
import redis
rs = redis.Redis("localhost")
rs.ping()
```

Should yield a 'True' response


### Running the services instance
    python ooiservices/manage.py runserver
    celery worker -A ooiservices.app.tasks -B
    
    Note: celery workers must be lauched in order to refresh the redis cache.

### To run the project using uWSGI (Production)
Remember to modify WSGI.py and app.ini to your specific installation environment
```
sudo mkdir /tmp/ooi-ui-services
sudo chown ooiui:nginx /tmp/ooi-ui-services
sudo chmod 755 /tmp/ooi-ui-services
```

Launch as a background process
```
uwsgi --ini app.ini &
```
    
### Service Tests
Test your initial setup by running from ooi-ui-services directory:
  
    python ooiservices/manage.py test

Verify you are getting data by using a web browser and navigating to:

    http://localhost:4000/arrays

----

This is the collection of services for the OOI UI.
