# http-waf

A simple http application to determine if a json request { is_malicious: true } ?

This app is written in Python3 and uses the Flask web framework.

# To Run and Test Locally:
1. Download or clone this repository.

2. From root project directory, install pip project dependencies by executing:
```
./bin/setup
```

3. To run locally, from root project directory execute:
```
./bin/start_server_local
```
///TODO maybe combine this into the same step
4. Then, to run unit tests and performance tests locally, from root project directory execute:
```
./bin/test_local
```

# To Run and Test Remotely:
1. Ensure pip project dependencies are installed by executing:
```
./bin/setup
```

2. To test remote deployment on heroku, from root project directory execute:
```
./bin/test_remote
```
which executes unit tests and performance tests on the remote deployment of the app.
(https://http-firewall-wren.herokuapp.com/)



# Notes on app.py
The application represents a simple http firewall that processes requests and returns either 200 OK or 403 Forbidden. If there is a request with a JSON body with a key named is_malicious (either at the root of the JSON object or nested in a child object), [which is set to True] then the request should generate a 403 Forbidden response.
Examples:
{
  "is_malicious": true,
} => 403 FORBIDDEN

{
  "hidden": { "is_malicious": true }
} => 403 Forbidden

{
  "is_malicious": false,
} => 200 OK

{
  "data": null
} => 200 OK

# handleRequest
The function handle-request, as you would expect, handles requests! It supports any method in order to generalize for any possible http request. It first checks whether unpacking the body returns a ValueError, which yields a success as their is no { "is_malicious": true }. Then it traverses the JSON body using the generator function traverse_object. Instead of returning, this generator yields values as they are needed and avoids storing the entire unpacked object in memory. This improves performance as if the is_malicious flag is set near the beginning of a large object, we will return 403 Forbidden as soon as it is found.

# Benchmark Results
The application was performance tested using pytest-benchmark. This library calls our server many times and provides a stastic summary of its running times. This allows us to see the mean time in ms for each request and the number of Operations Per Second.

The steps "To Run and Test Locally" yield the benchmark:
```
==================================================================================================================== test session starts =====================================================================================================================
platform darwin -- Python 3.6.2, pytest-6.1.2, py-1.9.0, pluggy-0.13.1
benchmark: 3.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /Users/gordonwren/Documents/Co-op/ThreatX/new_ismalicious_waf
plugins: benchmark-3.2.3
collected 15 items

tests_local/test_api.py .............                                                                                                                                                                                                                  [ 86%]
tests_local/test_api_perf.py ..                                                                                                                                                                                                                        [100%]


--------------------------------------------------------------------------------------------- benchmark: 2 tests --------------------------------------------------------------------------------------------
Name (time in ms)                             Min                   Max               Mean             StdDev            Median               IQR            Outliers       OPS            Rounds  Iterations
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_request_forbid_perf_benchmark         4.2010 (1.0)         13.8177 (1.0)       4.8915 (1.0)       0.8291 (1.0)      4.7447 (1.0)      0.5887 (1.0)           7;6  204.4362 (1.0)         168           1
test_massive_request_ok_perf_benchmark     4.4288 (1.05)     1,115.6780 (80.74)    10.3684 (2.12)     76.2757 (92.00)    4.9845 (1.05)     0.6576 (1.12)         1;12   96.4473 (0.47)        212           1
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
===================================================================================================================== 15 passed in 4.62s =====================================================================================================================
```









