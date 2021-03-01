import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Параметры сервера'},
    {'type': 'numeric',
     'title': 'Порт',
     'desc': 'Порт ТСР для доступа к серверу',
     'section': 'Network',
     'key': 'server_port'},
    {'type': 'string',
     'title': 'Адрес сервера',
     'desc': 'Адрес сервера',
     'section': 'Network',
     'key': 'server_address'},
])
