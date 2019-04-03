import json
import os
import urllib.request
import boto3

def format_message(data):
    parsed_arn = parse_arn(data.get('arn'))
    payload = {
        'username': 'Inspector',
        'icon_emoji': ':eye-in-speech-bubble:',
        'text': '{0} {1}'.format(get_mention(data.get('severity')), data.get('id')),
        'attachments': [
            {
                'fallback': 'Detailed information',
                'color': get_color(data.get('severity')),
                'text': data.get('title'),
                'fields': [
                    {
                        'title': 'AccountID',
                        'value': parsed_arn.get('account'),
                        'short': True
                    },
                    {
                        'title': 'Region',
                        'value': parsed_arn.get('region'),
                        'short': True
                    },
                    {
                        'title': 'Severity',
                        'value': data.get('severity'),
                        'short': True
                    }, 
                    {
                        'title': 'Timestamp',
                        'value': data.get('createdAt').strftime("%m/%d/%Y, %H:%M:%S%Z"),
                        'short': True
                    },
                    {
                        'title': 'Recommendation',
                        'value': data.get('recommendation'),
                        'short': False
                    }
                ]
            }
        ]
    }
    return payload

def get_mention(severity):
  if severity == "High":
    return '<!channel>'
  else:
    return ''

def get_color(severity):
  if severity == "High":
    return 'danger'
  else:
    return 'warning'

def parse_arn(arn):
    elements = arn.split(':', 5)
    result = {
        'arn': elements[0],
        'partition': elements[1],
        'service': elements[2],
        'region': elements[3],
        'account': elements[4],
        'resource': elements[5],
        'resource_type': None
    }
    if '/' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split('/',1)
    elif ':' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split(':',1)
    return result

def notify_slack(url, payload):
    data = json.dumps(payload).encode('utf-8')
    method = 'POST'
    headers = {'Content-Type': 'application/json'}

    request = urllib.request.Request(url, data = data, method = method, headers = headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')

def get_finding_detail(arn):
  client = boto3.client('inspector')
  finding = client.describe_findings(findingArns=[arn])['findings'][0]
  return finding

def get_finding_arn(event):
  message = event.get('Records')[0].get('Sns').get('Message')
  message = json.loads(message)
  return message.get('finding')

def lambda_handler(event, context):
    webhook_urls = os.environ['WEBHOOK_URLS']
    finding = get_finding_detail( get_finding_arn(event) )
    if not finding.get('severity') in ['HIGH', 'Medium']:
      return 'ignore finding of less than Medium'
    payload = format_message(finding)
    responses = []
    for webhook_url in webhook_urls.split(','):
      responses.append(notify_slack(webhook_url, payload))
    return responses
