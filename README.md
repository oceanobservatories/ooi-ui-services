ooi-ui-services
===============

Ocean Observatories Initiative - User Interface Services

## Services
The WSGI service endpoints are listed and defined below:

### Service Tests

* [asm](http://localhost:8845/service=alive)
* [c2](http://localhost:8846/service=alive)
* [notification](http://localhost:8847/service=alive)
* [science](http://localhost:8848/service=alive)
* [status](http://localhost:8849/service=alive)

### Service Endpoints

* Debug Information
  * Status
    * [checkconnections](http://localhost:8849/service=checkconnections)

* JSON Data Requests
  * [fetchstatus](http://localhost:8844/service=fetchstatus)
    * &sfplatform=
    * &sfinstrument=


