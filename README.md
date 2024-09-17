# 1. Заполнить config_export_ts.yaml 
### получить данные для переменных config_export_ts.yaml, делается на сервере core 
echo "
siem_api_secret_mpx = '$(cat /var/lib/deployer/role_instances/c*/params.yaml | grep ClientSecret | awk '{print $2}')'
"
# 2. Установить зависимости 
pip3 install -r requirements.txt

# 3. Запустить
python3 export_ts.py config_export_ts.yaml