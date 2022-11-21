# homework_bot
Бот-ассистент периодически проверяет состояние отправленных на проверку работ обращаясь к API обучающего ресурса. При обновлении статуса присылает сообщение в telegram. Безопасность токенов обеспечена через создание файла .env. В программе ведётся подробный лог работы бота.
## Технологии
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- REST API
## Запуск проекта локально:
Клонировать репозиторий и перейти в директорию с ним:
```
git clone git@github.com:Polina1Kostina/homework_bot.git
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Создать файл .env:
```
practicum_token = 'aaaaaaaaaaaaaaaa128' # токен полученный с обучающего сервиса
telegram_token = 'bbbbbbbbbbbbbbb025' #ваш телеграм-токен
```
Запустить проект:
```
python3 homework.py
```
## Авторы
[Полина Костина](https://github.com/Polina1Kostina) :eyes:
