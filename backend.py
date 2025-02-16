import logging

import flask
from flask import request
from terra.base_client import Terra

logging.basicConfig(level=logging.INFO)


_LOGGER = logging.getLogger("app")

app = flask.Flask(__name__)

webhook_secret = "328d323f83df49f5e7a44a7055d178cfc5420b073e60301d"
dev_id = '4actk-flowfit-testing-5d99i5FISY'
api_key = 'MIOWk0xEIQPMsVDM7UBbUEerTcyo72jq'

terra = Terra(api_key=api_key, dev_id=dev_id, secret=webhook_secret)

@app.route("/consumeTerraWebhook",methods=['POST'])
def consume_terra_webhook():
    body = request.get_json()

    verified = check_terra_signature(request.data.decode("utf-8"), request.headers['terra-signature'])

    if not verified:
        _LOGGER.info('NO')
        return flask.Response(status=403)

    _LOGGER.info("Received Terra Webhook: %s", body)

    return flask.Response(status=200)

@app.route('/authenticate', methods=['GET'])
def authenticate():
    #return terra.generate_widget_session(providers = ['CLUE','OURA'], reference_id = '1234').get_json()
    widget_response = terra.generate_widget_session(providers = ['CLUE','OURA'], reference_id = '1234')
    widget_url = widget_response.get_json()['url']
    return flask.Response(f"""
    <html>
        <body>
            <button onclick="window.location.href='{widget_url}';">
                Authenticate with Oura
            </button>
        </body>
    </html>
    """, mimetype="text/html")

if __name__ == "__main__":
    app.run()