# VPNProject     ПРОВЕРИТЬ НА АКТУАЛЬНОСТЬ
### Таблица с методами и описаниями:
|                                                                URL | Метод  |  Обязательный<br/>параметр<br/>command в теле запроса  | Описание                                                                                          |
|-------------------------------------------------------------------:|:------:|:------------------------------------------------------:|:--------------------------------------------------------------------------------------------------|
|                                                              user/ |  post  |                                                        | [Создание или обновление пользователя](#Создание или обновление пользователя)                     |
|                                                 user/<int: tg_id>/ |  get   |                                                        | [Получение данных о пользователе](#Получение данных о пользователе)                               |
|                        user/<int: tg_id>/vpn_keys/<str: srv_name>/ |  get   |                                                        | [Получение всех ключей конкретного пользователя](#Получение всех ключей конкретного пользователя) |
|                            vpn_token/<int: tg_id>/<str: srv_name>/ |  post  |         ```{"command": "create_demo_token"}```         | [Создание демо ключа](#Создание демо ключа)                                                       |
|                 vpn_token/<int: token_id>/refresh/<str: srv_name>/ |  post  |           ```{"command": "refresh_token"}```           | [Получение ключа взамен существующего](#Получение ключа взамен существующего)                     |
|                                         vpn_token/<str: srv_name>/ |  post  |         ```{"command": "create_new_token"}```          | [Создание нового ключа](#Создание нового ключа)                                                   |
|       vpn_token/<int: token_id>/user/<int: tg_id>/<str: srv_name>/ | patch  |         ```{"command": "add_user_to_token"}```         | [Привязка ключа к пользователю](#Привязка ключа к пользователю)                                   |
|                         vpn_token/<int: token_id>/<str: srv_name>/ | patch  |         ```{"command": "token_valid_date"}```          | [Изменение срока окончания действия ключа](#Изменение срока окончания действия ключа)             |
|                         vpn_token/<int: token_id>/<str: srv_name>/ | patch  |          ```{"command": "token_is_active"}```          | [Изменение имени ключа](#Изменение имени ключа)                                                   |
|                         vpn_token/<int: token_id>/<str: srv_name>/ | patch  |            ```{"command": "token_name"}```             | [Изменение статуса ключа](#Изменение статуса ключа)                                               |
|                         vpn_token/<int: token_id>/<str: srv_name>/ | patch  |        ```{"command": "token_traffic_limit"}```        | [Изменение лимита траффика ключа](#Изменение лимита траффика ключа)                               |
|                         vpn_token/<int: token_id>/<str: srv_name>/ | delete |                                                        | [Удаление ключа](#Удаление ключа)                                                                 |


## Описание работы API:

### Создание или обновление пользователя

URL: user/
METHOD: POST
BODY:
```json
{ 
  "user": {
    "id": "integer",
    "first_name": "string or None",
    "last_name": "string or None",
    "username": "string or None"
    }
}
```
RESPONSE: 200
```json
{
  "status": 200,
  "details":  "create or update user successful"
}
```

### Получение данных о пользователе
URL: user/<int: tg_id>/
METHOD: GET

RESPONSE: 200
```json
{
  "telegram_id": "integer", 
  "telegram_login": "string or None",
  "telegram_first_name": "string or None",
  "telegram_last_name": "string or None",
  "is_admin": "Boolean",
  "created_at": "datetime"
}
```

### Создание демо ключа
URL: vpn_token/<int: tg_id>/<str: srv_name>/
METHOD: POST

BODY:
```json
{
"command": "create_demo_token"
}
```

RESPONSE: 201
```json
{
  "vpn_keys": {
    "outline_key_id": "integer", 
    "outline_key_name": "string or None",
    "outline_key_value": "string or None",
    "outline_key_valid_until": "string or None",
    "outline_key_active": "Boolean",
    "telegram_user_record": "Boolean",
    "created_at": "datetime"
    }
}
```

### Получение всех ключей конкретного пользователя
URL: user/<int: tg_id>/vpn_keys/<str: srv_name>/
METHOD: GET

RESPONSE: 200
```json
{
  "vpn_keys": [{
    "outline_key_id": "integer", 
    "outline_key_name": "string or None",
    "outline_key_value": "string or None",
    "outline_key_valid_until": "string or None",
    "outline_key_active": "Boolean",
    "telegram_user_record": "Boolean",
    "created_at": "datetime"
    }, 
    {}
  ]
}
```


### Получение ключа взамен существующего
URL: vpn_token/<int: token_id>/refresh/<str: srv_name>/
METHOD: POST
BODY:
```json
{
"command": "refresh_token"
}
```

RESPONSE: 201
```json
{
  "vpn_keys": {
    "outline_key_id": "integer", 
    "outline_key_name": "string or None",
    "outline_key_value": "string or None",
    "outline_key_valid_until": "string or None",
    "outline_key_active": "Boolean",
    "telegram_user_record": "Boolean",
    "created_at": "datetime"
    }
}
```