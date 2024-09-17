import requests
import json
from datetime import datetime, timedelta
import pytz
from urllib.parse import quote
import pandas as pd
import yaml
import sys
import warnings

# Чтение файла конфигурации
with open(sys.argv[1], 'r', encoding='utf-8') as file:
    config_siem = yaml.safe_load(file)

username = config_siem['username']
password = config_siem['password']
encoded_data = quote(password)
client_id = 'mpx'
siem_api_secret_mpx = config_siem['siem_api_secret_mpx']
grant_type = 'password'
response_type = 'code%20id_token'
scope = 'mpx.api'
base = config_siem['base']
default_days = config_siem['default_days']
ts_name = config_siem['ts_name']

# Получение токена доступа
url = f"https://{base}:3334/connect/token"
payload = f'username={username}&password={encoded_data}&client_id={client_id}&client_secret={siem_api_secret_mpx}&grant_type={grant_type}&response_type={response_type}&scope={scope}'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}
with warnings.catch_warnings():
    warnings.simplefilter("ignore") 
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

data = json.loads(response.text)
access_token = data['access_token']

url_tables = f"https://{base}/api/events/v2/table_lists/"
headers = {
  'Authorization': f'Bearer {access_token}'
}
# Получение всех табличных списков
with warnings.catch_warnings():
    warnings.simplefilter("ignore") 
    response_table_list = requests.request("GET", url_tables, headers=headers, verify=False)

data_tasks = json.loads(response_table_list.text)

# Получение токена (id) табличного списка
token = ''
for i in range(len(data_tasks)):

    if (data_tasks[i]['name']) == ts_name:
      token=data_tasks[i]["token"]


# Получение данных из табличного списка
url_ts = f"https://{base}/api/events/v2/table_lists/{token}/content/search"
payload = json.dumps(
{
  "offset": 0,
  "limit": 50,
  "filter": {
    "select": "",
    "where": "",
    "orderBy": [
      {
        "field": "_last_changed",
        "sortOrder": "descending"
      }
    ],
    "timeZone": 180,
    "stringDatetime": True
  }
})
headers = {
  'Authorization': f'Bearer {access_token}',
  'Content-Type': 'application/json'
}
with warnings.catch_warnings():
    warnings.simplefilter("ignore") 
    response_ts = requests.request("POST", url_ts, headers=headers, data =payload, verify=False)

data_ts = json.loads(response_ts.text)

data_ts_items = data_ts['items']
data_end = []
# Получение даты из табличного списка и сравнение с полученной
for i in range(len(data_ts_items)):

  time = data_ts_items[i]['_last_changed']
  time_object = datetime.fromisoformat(time)

  days_ago = datetime.now(pytz.timezone('UTC')) - timedelta(days=default_days)
  if time_object > days_ago:
    data_end.append(data_ts_items[i])

# Запись табличного списка
if (len(data_end)!=0):
  df = pd.DataFrame(data_end)
  df.to_csv(f'{ts_name}.csv', index=False, sep=';')
  print(f"Выгрузка выполнена: {ts_name}.csv")