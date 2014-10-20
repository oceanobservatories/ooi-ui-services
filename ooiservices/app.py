from flask import Flask
from flask.ext import restful

from controller.platform import PlatformController

app = Flask(__name__)
api = restful.Api(app)

# endpoints
api.add_resource(PlatformController.List, '/platforms')
api.add_resource(PlatformController, '/platforms/<string:id>')

if __name__ == '__main__':
    app.run(debug=True)
