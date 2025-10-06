# [START gae_python312_app]
# [START gae_python3_app]
import logging
import re
import subprocess
import flask

iphostregex = re.compile(
    r'([A-Z0-9][A-Z0-9-]{0,61}\.)*[A-Z0-9][A-Z0-9-]{0,61}', re.IGNORECASE
)
urlregex = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
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


@app.route('/hello')
def hello():
  """Return a friendly HTTP greeting.

  Returns:
      A string with the words 'Hello World!'.
  """
  user = flask.request.args.get('user', 'World')
  return 'Hello {}!'.format(user)


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
