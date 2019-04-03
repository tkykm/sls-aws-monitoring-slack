import json
import os
import urllib.request

def format_message(data):
    severity_level = get_severity_level(data['detail']['severity'])
    payload = {
        'username': 'GuardDuty Finding',
        'icon_emoji': ':guardduty:',
        'text': '{} GuardDuty Finding in {}'.format(severity_level['mention'], data['detail']['region']),
        'attachments': [
            {
                'fallback': 'Detailed information on GuardDuty Finding.',
                'color': severity_level['color'],
                'title': data['detail']['title'],
                'text': data['detail']['description'],
                'fields': [
                    {
                        'title': 'Account ID',
                        'value': data['detail']['accountId'],
                        'short': True
                    },
                    {
                        'title': 'Severity',
                        'value': severity_level['label'],
                        'short': True
                    },
                    {
                        'title': 'Type',
                        'value': data['detail']['type'],
                        'short': False
                    }
                ]
            }
        ]
    }
    return payload

def get_severity_level(severity):
    # ref: http://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html#guardduty_findings-severity
    if severity == 0.0:
        level = {'label': 'Information', 'color': 'good', 'mention': ''}
    elif 0.1 <= severity <= 3.9:
        level = {'label': 'Low', 'color': 'warning', 'mention': ''}
    elif 4.0 <= severity <= 6.9:
        level = {'label': 'Medium', 'color': 'warning', 'mention': '<!here>'}
    elif 7.0 <= severity <= 8.9:
        level = {'label': 'High', 'color': 'danger', 'mention': '<!channel>'}
    elif 9.0 <= severity <= 10.0:
        level = {'label': 'Critical', 'color': 'danger', 'mention': '<!channel>'}
    else:
        level = {'label': 'Unknow', 'color': '#666666', 'mention': ''}
    return level

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
    responses = []
    for webhook_url in webhook_urls.split(','):
      responses.append( notify_slack(webhook_url, payload) )
    return responses
