import requests
import json


def lambda_handler(event, context):
  key = 'eeb1ed6ba9bffdf874ccf3e9373e26b3'
  r = requests.get('https://2captcha.com/res.php?key='+key+'&action=getbalance')
  b = float(r.text)
  return {
    'statusCode': 200,
    'body': json.dumps(b)
  }

