from flask import Flask, request, jsonify
from flask_api import status
import sys
import json

# A simple HTTP service that will accept requests
# and return either 200 OK or 403 Forbidden.

# Malicious requests will announce their intent in the body.
# If there is a request with a JSON body with a key named is_malicious
#   (either at the root of the JSON object or nested in a child object)
# then the request should generate a 403 Forbidden response. For example:
#   { "is_malicious": true } and { "hidden": { "is_malicious": true } } => 403 Forbidden
#   { "is_malicious": false } and { "data": null } => 200 OK

app = Flask(__name__)
app.config["DEBUG"] = True

success = {"status": "success", "code": 200,
           "message": ""}  # success response body
forbidden = {"status": "error", "code": 403,
             "message": "is_malicious found"}  # forbidden response body
IS_MALICIOUS = "is_malicious"


@app.route('/', methods=['GET'])
def home():
    return """<h1>Simple Web Application Firewall</h1>
                    <p>A simple HTTP service that will accept requests and return either 200 OK or 403 Forbidden</p>
                    <p>To scan a request for "is_malicious" send POST request to .../api/handle-request</p>
                    <p> ex: localhost:5000/api/handle-request with request body { "is_malicious": true } </p>"""


# Function to handle 404 errors.
# Simply displays
@app.errorhandler(404)
def page_not_found(e):
    return """<h1>404</h1><p>The resource could not be found.</p>
                <p>To scan a request for "is_malicious" send POST request to .../api/handle-request</p>
                    <p> ex: localhost:5000/api/handle-request with request body { "is_malicious": true } </p>""", 404

# Function to act as Web Application Firewall, handles http requests.
# if request body contains { "is_malicious": true }
#   returns 403 Forbidden
# else returns 200 Ok
#
# Function/Assignment acts as a firewall so should handle all methods with a body (all methods can have body per RFCs 7230-7237)
@app.route('/api/handle-request', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
def handleRequest():
    try:  # try to deserialize request body
        req_data = request.get_json()  # convert the JSON object into Python data for us
    except ValueError:  # if no text or bad format
        return success  # return 200 OK as there is no { "is_malicious": true }

    # iterate through the object recursively to get all (key, value) pairs in nested object
    for key, value in traverse_object(req_data):

        # if the key == "is_malicious" and the value is True
        if key == IS_MALICIOUS and value == True:
            # return informative forbidden object with status code 403 FORBIDDEN
            return forbidden, status.HTTP_403_FORBIDDEN

    # return informative success object with status code 200 OK
    return success, status.HTTP_200_OK


# a generator function to find key value pairs with a depth first search order.
# Generator computes values as needed rather than computing them all at once and returning as a list.
# input: Object
# output: list of key, value pairs
# key - a key or index in object mapped to a value
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
# execution output:
# ('language', 'Python')
# ('framework', 'Flask')
# ('website', 'Scotch')
# ('python', 3.4)
# ('flask', 0.12)
# ('is_malicious', 'false')
# (1, 'form')
# (2, 'json')
# ('boolean_test', True)
def traverse_object(obj, parent_key=None):
    if isinstance(obj, dict):  # if the object is a dictionary
        for key, value in obj.items():  # for each key value pair in the dictionary
            # keep yielding key,value pairs as needed recursively
            yield from traverse_object(value, key)
    elif isinstance(obj, list):  # if the object is a list
        for idx, item in enumerate(obj):  # for each index, item in the list
            # recursively traverse each object in list
            yield from traverse_object(item, idx)
    else:
        # else(basecase), the obj is not a dict or list just yield the simple parent_key, object pair
        yield parent_key, obj



if __name__ == '__main__': # encapsulate the run
    app.run(debug=True) # start the app
