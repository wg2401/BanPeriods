import logging

import flask
from flask import request
from terra.base_client import Terra

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request

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

    verified = terra.check_terra_signature(request.data.decode("utf-8"), request.headers['terra-signature'])

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


# ffb7fd43-e937-4bae-beed-0903b3a98c7c
'''
@app.route('/backfill', methods=['GET'])
def backfill():
    user_id = 'ffb7fd43-e937-4bae-beed-0903b3a98c7c'
    
    terra_user = terra.from_user_id(user_id)

    terra_user.get_menstruation
'''

app = FastAPI()

TERRA_API_URL = "https://api.tryterra.co/v2"  # Ensure this is correct

@app.route("/webhook", methods=['POST'])
def webhook_handler():
    payload = request.get_json()

    if payload.get("type") == "auth" and payload.get("status") == "success":
        user_id = payload.get("user_id")  # Extract user ID from webhook
        if not user_id:
            return {"message": "User ID not found in webhook payload"}

        # Calculate date range: past 28 days up to today
        start_date = (datetime.utcnow() - timedelta(days=28)).strftime('%Y-%m-%d')
        end_date = datetime.utcnow().strftime('%Y-%m-%d')

        headers = {
            "x-api-key": "MIOWk0xEIQPMsVDM7UBbUEerTcyo72jq", 
            "dev-id": "4actk-flowfit-testing-5d99i5FISY"
        }

        endpoints = ["/menstruation"]  # Fetch menstruation data
        results = {}

        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"https://api.tryterra.co/v2{endpoint}",
                    headers=headers,
                    params={
                        "user_id": user_id,  # Fetch for a specific user
                        "start_date": start_date,
                        "end_date": end_date,
                        "to_webhook": False  # Return data immediately
                    },
                    timeout=10  # Avoid hanging requests
                )
                response.raise_for_status()
                results[endpoint] = response.json()
            except requests.exceptions.RequestException as e:
                results[endpoint] = {"error": str(e)}  # Return partial data if error occurs

        return {"message": "User data fetched successfully", "data": results}

    return {"message": "Webhook type or status did not match criteria", "received_payload": payload}


if __name__ == "__main__":
    app.run()