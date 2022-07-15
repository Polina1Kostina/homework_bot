import time
import requests
from dotenv import load_dotenv
import telegram
import logging
import sys
import os

load_dotenv()

PRACTICUM_TOKEN = os.getenv('practicum_token')
TELEGRAM_TOKEN = os.getenv('telegram_token')
TELEGRAM_CHAT_ID = 632833609

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    logger.debug('Начата отправка сообщения в Telegram')
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
    )
    logger.info('Удачная отправка ообщения в Telegram')


def get_api_answer(current_timestamp):
    """Вовзвращает ответ API с типом данных Python."""
    timestamp = current_timestamp or int(time.time())
    print(timestamp)
    params = {'from_date': timestamp}
    logger.debug(f'Запрос к адресу {ENDPOINT} запущен')
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise OSError('Статус код запроса не равен 200')
    response = response.json()
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.debug('Начата проверка ответа API на корректность')
    if type(response['homeworks']) != list:
        raise TypeError('Тип данных homeworks - не лист')
    if 'homeworks' not in response:
        logger.error('Ответ API не содержит ключ homeworks')
        raise Exception('В словаре нет homeworks')
    if len(response) == 0:
        raise Exception('Слишком пусто!')
    return response


def parse_status(homework):
    """Возвращает подготовленную для отправки в Telegram строку."""
    try:
        homework_name = homework.get('homework_name')
    except Exception:
        message = 'Домашняя работа с таким названием отсутствует в ответе API'
        logger.error(message)
        raise KeyError(message)
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_STATUSES.keys():
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        message = 'Статус домашней работы отсутствует в ответе API'
        logger.error(message)
        raise KeyError(message)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID is not None:
        return True
    else:
        logger.critical(
            'Отсутствие обязательных переменных окружения'
            'во время запуска бота'
        )
        return False


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(msg)s'
        ' - %(message)s',
        level=logging.DEBUG
    )
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1634074965
    print(current_timestamp)
    check_tokens()
    prev_report = {}
    current_report = {'1': 1}
    while True:
        try:
            response = requests.get(
                ENDPOINT, headers=HEADERS, params={
                    'from_date': current_timestamp
                }
            )
            response = get_api_answer(current_timestamp)
            check_response(response)
            print(response)
            current_timestamp = response['current_date']
            try:
                logger.debug('Начат запрос базы')
                homework = response['homeworks'][0]
            except Exception as error:
                logger.error(f'Ошибка при запросе к {ENDPOINT}: {error}')
            try:
                message = parse_status(homework)
            except Exception:
                logging.error('Cбой при формировании сообщения в Telegram')
            if current_report != prev_report:
                try:
                    send_message(bot, message)
                except Exception:
                    logging.error('Cбой при отправке сообщения в Telegram')
                else:
                    logger.info('Удачная отправка ообщения в Telegram')
                prev_report = current_report.copy()
            else:
                logger.info('Нет новых статусов')
            current_report = {
                'name': homework.get('homework_name'),
                'message': message,
            }
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)
        else:
            None


if __name__ == '__main__':
    main()
