import json
import boto3
import cr_response

def lambda_handler(event, context):
  try:
    params = dict([(k, v) for k, v in event['ResourceProperties'].items() if k != 'ServiceToken'])
    client = boto3.client('inspector')
    if event['RequestType'] == 'Create':
      response_data = client.subscribe_to_event(**params)
    if event['RequestType'] == 'Delete':
      response_data = client.unsubscribe_from_event(**params)
    if event['RequestType'] == 'Update':
      old_params = dict([(k, v) for k, v in event['OldResourceProperties'].items() if k != 'ServiceToken'])
      client.unsubscribe_from_event(**old_params)
      response_data = client.subscribe_to_event(**params)
    print(response_data)
    lambda_response = cr_response.CustomResourceResponse(event, context)
    lambda_response.respond()
  except Exception as e:
    lambda_response.respond_error(e)
    raise e
