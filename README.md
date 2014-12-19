[![Build Status](https://travis-ci.org/asascience-open/ooi-ui-services.svg?branch=master)](https://travis-ci.org/asascience-open/ooi-ui-services)

ooi-ui-services
===============

Ocean Observatories Initiative - User Interface Services

## Services
The WSGI service endpoints are listed and defined below:
Active Routes for Listing:

    /arrays
    /platform_deployments
        /platform_deployments?array_code=
    /instrument_deployments
        /instrument_deployments?platform_deployment_code=
    /streams
        /streams?instrument_id=

Active Routes for specific item deployment inspection:

    /arrays/<array_code>
    /platform_deployments/<ref:id>
    /instrument_deployments/<ref:id>
    /streams/<ref:id>
    
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

    You'll need Postgis.

Create and load your database.  Service assumes no password for default postgres user:

    psql -c 'create database ooi_ui;' -U postgres
    psql -c 'create database ooi_asset;' -U postgres
    psql -c 'create database ooi_user_management;' -U postgres
    psql -U postgres ooi_ui -c "create extension postgis;"
    psql ooi_ui < db/ooi_ui_schema.sql
    psql ooi_ui < db/ooi_ui_bulk_load.sql

### Service Tests
Run your service by evoking the following command from your ooi-ui-services directory:
  
    PYTHONPATH=. python ooiservices/app.py

Verify you are getting data by using a web browser and navigating to:

    http://localhost:4000/arrays

### Service Endpoints

* Debug Information
  * Status
    * TBD

* JSON Data Requests
  * TDB


----

This is the backend for the OOI UI
