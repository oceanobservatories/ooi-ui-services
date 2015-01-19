[![Build Status](https://travis-ci.org/asascience-open/ooi-ui-services.svg?branch=master)](https://travis-ci.org/asascience-open/ooi-ui-services)

ooi-ui-services
===============

Ocean Observatories Initiative - User Interface Services

## Services
The WSGI service endpoints are listed and defined below:
Active Routes for Listing:

    /arrays
    /platform_deployments
        /platform_deployments?array_id=
    /instrument_deployments
        /instrument_deployments?platform_deployment_id=
    /streams
        /streams?instrument_id=

Active Routes for specific item deployment inspection:

    /arrays/<string:array_code>
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
    pip install -r requirements.txt

Setup your PostgreSQL environment:
    install postgis...

###If you are using a local database instance
Create and load your database.  Service assumes no password for default postgres user:

    Setup dev db:
    psql -c "create database ooiuidev;" -U postgres
    psql -c "create extension postgis;" ooiuidev
    psql -c "create schema ooiui;" ooiuidev
    python ooiservices/manage.py deploy --password <string:admin_password>
    psql ooiuidev < db/ooiui_schema_before_data.sql
    psql ooiuidev < db/ooiui_schema_data.sql
    psql ooiuidev < db/ooiui_schema_after_data.sql
    
    Setup test db:
    psql -c "create database ooiuitest;" -U postgres
    psql -c "create extension postgis;" ooiuitest
    psql -c "create schema ooiui;" ooiuitest
    psql ooiuidev < db/ooiui_schema_before_data.sql
    psql ooiuidev < db/ooiui_schema_data.sql
    psql ooiuidev < db/ooiui_schema_after_data.sql

### Service Tests
Test your initial setup by running from ooi-ui-services directory:
  
    python ooiservices/manage.py test
    
Run your service by evoking the following command from your ooi-ui-services directory:
  
    python ooiservices/manage.py runserver

Verify you are getting data by using a web browser and navigating to:

    http://localhost:4000/arrays

----

This is the backend for the OOI UI
