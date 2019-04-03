import json
import os
import urllib.request

def format_message(data):
    payload = {
        'username': 'Trusted Advisor',
        'icon_emoji': ':police_car:',
        'text': '{} {}'.format(get_mention(data['detail']['status']), data['detail-type']),
        'attachments': [
            {
                'fallback': 'Detailed information',
                'color': get_color(data['detail']['status']),
                'title': data['detail']['check-name'],
                'text': "```\n{0}\n```".format(data['detail']['check-item-detail']),
                'fields': [
                    {
                        'title': 'Account ID',
                        'value': data['account'],
                        'short': True
                    },
                    {
                        'title': 'Status',
                        'value': data['detail']['status'],
                        'short': True
                    },
                    {
                        'title': 'ARN',
                        'value': data['detail']['resource_id'],
                        'short': True
                    },
                    {
                        'title': 'Region',
                        'value': data['detail']['check-item-detail']['Region'] if 'Region' in data['detail']['check-item-detail'] else "",
                        'short': True
                    }
                ]
            }
        ]
    }
    return payload

def get_color(status):
  color = '#666666'  
  if status == 'ERROR':
    color = 'danger'
  elif status == 'WARN':
    color = 'warning'
  return color

def get_mention(status):
  if status == 'ERROR':
    return '<!channel>'
  else:
    return ''

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
    if event['detail'].get('check-name') == "Amazon EBS Snapshots":
      return None
    responses = []
    for webhook_url in webhook_urls.split(','):
      responses.append(notify_slack(webhook_url, payload))
    return responses
