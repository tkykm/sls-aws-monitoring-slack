import json
import os
import urllib.request

def format_message(data):
    payload = {
        'username': 'Budget',
        'icon_emoji': ':moneybag:',
        'text': '<!channel> Budget exceed threshold alert',
        'attachments': [
            {
                'fallback': 'Detailed information',
                'color': "danger",
                'title': data['Sns']['Subject'],
                'text': data['Sns']['Message'],
            }
        ]
    }
    return payload

def notify_slack(url, payload):
    data = json.dumps(payload).encode('utf-8')
    method = 'POST'
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, data = data, method = method, headers = headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')

def lambda_handler(event, context):
    webhook_urls = os.environ['WEBHOOK_URLS']
    payload = format_message(event['Records'][0])
    responses = []
    for webhook_url in webhook_urls.split(','):
      responses.append(notify_slack(webhook_url, payload))
    return responses
