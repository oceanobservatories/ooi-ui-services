[![Build Status](https://travis-ci.org/asascience-open/ooi-ui-services.svg?branch=master)](https://travis-ci.org/asascience-open/ooi-ui-services)

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
    
Usage:
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
    
Setup the Database:
    python ooiservices/manage.py deploy --password <admin-password>


### Debugging Database Problems

If you attempt to deploy the database `ooiservices/manage.py deploy` and
encounter an error "role postgres does not exist". You need to create the role
postgres. You can do so by

```
psql postgres
CREATE ROLE postgres LOGIN SUPERUSER;
```

### Running the services instance
    python ooiservices/manage.py runserver
    
### Service Tests
Test your initial setup by running from ooi-ui-services directory:
  
    python ooiservices/manage.py test

Verify you are getting data by using a web browser and navigating to:

    http://localhost:4000/arrays

----

This is the backend for the OOI UI
