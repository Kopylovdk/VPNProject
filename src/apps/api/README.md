# VPNProject
### Таблица с методами и описаниями:
|                                                                URL | Метод  | Обязательный<br/>параметр<br/>command в теле запроса | Описание                                                                                          |
|-------------------------------------------------------------------:|:------:|:----------------------------------------------------:|:--------------------------------------------------------------------------------------------------|
|                                                          api/user/ |  post  |                                                      | [Создание или обновление пользователя](#Создание или обновление пользователя)                     |
|                                             api/user/<int: tg_id>/ |  get   |                                                      | [Получение данных о пользователе](#Получение данных о пользователе)                               |
|                    api/user/<int: tg_id>/vpn_keys/<str: srv_name>/ |  get   |                                                      | [Получение всех ключей конкретного пользователя](#Получение всех ключей конкретного пользователя) |
|                        api/vpn_token/<int: tg_id>/<str: srv_name>/ |  post  |           {'command': 'create_demo_token'}           | [Создание демо ключа](#Создание демо ключа)                                                       |
|             api/vpn_token/<int: token_id>/refresh/<str: srv_name>/ |  post  |             {'command': 'refresh_token'}             | [Получение ключа взамен существующего](#Получение ключа взамен существующего)                     |
|                                     api/vpn_token/<str: srv_name>/ |  post  |           {'command': 'create_new_token'}            | [Создание нового ключа](#Создание нового ключа)                                                   |
|   api/vpn_token/<int: token_id>/user/<int: tg_id>/<str: srv_name>/ | patch  |           {'command': 'add_user_to_token'}           | [Привязка ключа к пользователю](#Привязка ключа к пользователю)                                   |
|                     api/vpn_token/<int: token_id>/<str: srv_name>/ | patch  |           {'command': 'token_valid_date'}            | [Изменение срока окончания действия ключа](#Изменение срока окончания действия ключа)             |
|                     api/vpn_token/<int: token_id>/<str: srv_name>/ | patch  |            {'command': 'token_is_active'}            | [Изменение имени ключа](#Изменение имени ключа)                                                   |
|                     api/vpn_token/<int: token_id>/<str: srv_name>/ | patch  |              {'command': 'token_name'}               | [Изменение статуса ключа](#Изменение статуса ключа)                                               |
|                     api/vpn_token/<int: token_id>/<str: srv_name>/ | patch  |          {'command': 'token_traffic_limit'}          | [Изменение лимита траффика ключа](#Изменение лимита траффика ключа)                               |
|                     api/vpn_token/<int: token_id>/<str: srv_name>/ | delete |                                                      | [Удаление ключа](#Удаление ключа)                                                                 |


## Описание работы API:

### Создание или обновление пользователя:

URL: api/user/
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
RESPONSE:
```json
{
  "status": 200,
  "details":  "create or update user successful"
}
```

### Получение данных о пользователе


###