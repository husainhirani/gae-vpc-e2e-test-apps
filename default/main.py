# [START gae_python312_app]
# [START gae_python3_app]
"""This app is used to test VPC perimeters from a GAE Standard environment.

It includes an endpoint to test external connectivity using cURL.
"""
import logging
import re
import subprocess
import flask

iphostregex = re.compile(
    r'([A-Z0-9][A-Z0-9-]{0,61}\.)*[A-Z0-9][A-Z0-9-]{0,61}', re.IGNORECASE
)
urlregex = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = flask.Flask(__name__)

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VPC E2E Test Application</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>">
    <style>
        body {
            font-family: sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #0056b3;
            text-align: center;
        }
        button {
            display: block;
            margin: 20px auto;
            padding: 12px 25px;
            font-size: 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #0056b3;
        }
        pre {
            background-color: #eee;
            padding: 15px;
            border-radius: 5px;
            overflow-wrap: break-word;
            white-space: pre-wrap;
            border: 1px solid #ddd;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>VPC E2E Test Application</h1>
    <button id="testButton">Test External Endpoint</button>
    <h2>Result:</h2>
    <pre id="result">Click the button to run the test...</pre>
    <script>
        document.getElementById('testButton').addEventListener('click', function(event) {
            const resultElement = document.getElementById('result');
            resultElement.textContent = 'Loading...';
            fetch('/external')
                .then(response => response.text())
                .then(data => {
                    resultElement.textContent = data;
                })
                .catch(error => {
                    resultElement.textContent = 'Error: ' + error;
                });
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
  return UI_HTML


@app.route('/external')
def test_external_endpoint():
  """Tests an external endpoint by making a cURL request.

  The URL to test is provided via the 'url' query parameter.
  The function logs the cURL output and returns it in a plain text response.

  Returns:
      A flask.Response object containing the cURL command and its output,
      or a string 'Invalid URL' if the provided URL is not valid.
  """
  url = flask.request.args.get('url')

  if url is None:
    url = 'https://www.google.com/humans.txt'

  if re.match(urlregex, url) is None:
    return 'Invalid URL'
  logging.info('Entering DoHTTP')
  logging.info('---- Invoking cURL ----')
  process = subprocess.Popen(
      ['/bin/sh', '-c', 'curl --silent --verbose ' + url + ' 2>&1'],
      stdout=subprocess.PIPE,
  )
  output = ''
  if process.stdout:
    output = process.stdout.read().decode('utf-8')
  logging.info(output)
  rc = process.wait()
  logging.info('Subprocess Returned: %s', rc)
  resp = flask.Response()
  resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
  resp.data = 'curl --silent --verbose ' + url + '\n\n' + output
  return resp


if __name__ == '__main__':
  # This is used when running locally only. When deploying to Google App
  # Engine, a webserver process such as Gunicorn will serve the app. You
  # can configure startup instructions by adding `entrypoint` to app.yaml.
  app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python312_app]
