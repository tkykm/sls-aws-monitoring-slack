import json
import os
import urllib.request

def format_message(data):
    accountid = data['accountId']
    data['invokingEvent'] = json.loads(data["invokingEvent"])
    if not 'configurationItemDiff' in data['invokingEvent']:
      print(data)
      return None
    diff = data['invokingEvent'].get('configurationItemDiff')
    if not diff:
      return None
    configurationitem = data['invokingEvent'].get('configurationItem')
    if not configurationitem:
      print(data)
      return None
    payload = {
        'username': 'AWS Config',
        'icon_emoji': ':camera:',
        'text': '',
        'attachments': [
            {
                'fallback': 'Summary',
                'color': '#439FE0',
                'title': data['invokingEvent'].get('messageType'),
                'fields': [
                    {
                        'title': 'Account ID',
                        'value': accountid,
                        'short': True
                    },
                    {
                        'title': 'ARN',
                        'value': configurationitem.get('ARN'),
                        'short': True
                    },
                    {
                        'title': 'changeType',
                        'value': diff.get('changeType'),
                        'short': True
                    },
                    {
                        'title': 'Region',
                        'value': configurationitem.get('awsRegion'),
                        'short': True
                    }
                ]
            },
            {
                "title": 'configuration',
                "fallback": "Detail",
                "color": "#439FE0",
                "text": "```\n{0}\n```".format(data['invokingEvent'])
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
    payload = format_message(event)
    if not payload:
      return None
    responses = []
    for webhook_url in webhook_urls.split(','):
      responses.append( notify_slack(webhook_url, payload) )
    return responses

