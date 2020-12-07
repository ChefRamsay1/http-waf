from flask import Flask, request, jsonify
from flask_api import status
import sys
import json

app = Flask(__name__)
app.config["DEBUG"] = True

# A simple HTTP service that will accept requests
# and return either 200 OK or 403 Forbidden.

# Malicious requests will announce their intent in the body.
# If there is a request with a JSON body with a key named is_malicious
#   (either at the root of the JSON object or nested in a child object)
# then the request should generate a 403 Forbidden response. For example:
#   { "is_malicious": true } and { "hidden": { "is_malicious": true } } => 403 Forbidden
#   { "is_malicious": false } and { "data": null } => 200 OK

success = {"status": "success", "code": 200, "message": ""}  # success response body
forbidden = {"status": "error", "code": 403, "message": "is_malicious found"}  # forbidden response body
IS_MALICIOUS = "is_malicious"

home_page_html = """<h1>Simple Web Application Firewall</h1>
                    <p>A simple HTTP service that will accept requests and return either 200 OK or 403 Forbidden</p>
                    <p>To scan a request for "is_malicious" send POST request to /api/handle-request</p>"""


@app.route('/', methods=['GET'])
def home():
    return """<h1>Simple Web Application Firewall</h1>
                    <p>A simple HTTP service that will accept requests and return either 200 OK or 403 Forbidden</p>
                    <p>To scan a request for "is_malicious" send POST request to /api/handle-request</p>
                    <p> ex: localhost:5000/api/handle-request with request body { "is_malicious": true } </p>"""

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

# returns 403 Forbidden if request body contains { "is_malicious": true } anywhere
# otherwise returns 200 Ok
@app.route('/api/handle-request', methods=['HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def handleRequest():
    try:  # try to deserialize request body
        req_data = request.get_json()  # convert the JSON object into Python data for us
    except ValueError:  # if no text or bad format
        return success  # return 200 OK as there is no { "is_malicious": true }


    # iterate through the object recursively to get all ((key, key,..), value) in nested object
    for key, value in traverse_object(req_data):
        
        # if the key == "is_malicious" and the value is True
        if key == IS_MALICIOUS and value == True:
            return forbidden, status.HTTP_403_FORBIDDEN

    return success, status.HTTP_200_OK


# a generator function to return key value pairs with a depth first search order
# input: Object
# output: list of keys, value pairs
# keys - list of keys navigating the object to the value
# value - value in the object that is not a dictionary, list, or tuple
# example:
# input: 
# {
#     "language" : "Python",
#     "framework" : "Flask",
#     "website" : "Scotch",
#     "version_info" : {
#         "python" : 3.4,
#         "flask" : 0.12
#     },
#     "examples" : [{ "is_malicious": {"is_malicious": "false"}}, "form", "json"],
#     "boolean_test" : true
# }
# output: 
# (('language',), 'Python')
# (('framework',), 'Flask')
# (('website',), 'Scotch')
# (('version_info', 'python'), 3.4)
# (('version_info', 'flask'), 0.12)
# (('examples', 0, 'is_malicious', 'is_malicious'), 'false')
# (('examples', 1), 'form')
# (('examples', 2), 'json')
# (('boolean_test',), True)
def traverse_object(obj, parent_key=None):
    if isinstance(obj, dict):  # if the object is a dictionary
        for key, value in obj.items():  # for each key value pair in the dictionary
            yield from traverse_object(value, key)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            yield from traverse_object(item, idx)
    else:
        yield parent_key, obj


app.run()
