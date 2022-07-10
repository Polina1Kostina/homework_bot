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
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except Exception:
        logging.error('Cбой при отправке сообщения в Telegram')
    logger.info('Удачная отправка ообщения в Telegram')


def get_api_answer(current_timestamp):
    """Вовзвращает ответ API с типом данных Python."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        homework = response.json()
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != 200:
        raise OSError('Статус код запроса не равен 200')
    return homework


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        response.raise_for_status()
    except Exception:
        logger.error('Ответ API некорректен')
    if 'homeworks' not in response:
        logger.error('Ответ API не содержит ключ homeworks')
    if type(response['homeworks']) != list:
        raise TypeError('Тип данных ответа с ключом "homeworks" не лист')
    return response['homeworks']


def parse_status(homework):
    """Возвращает подготовленную для отправки в Telegram строку."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
    except Exception:
        logger.error('Отсутствие ожидаемых ключей в ответе API')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


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
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = requests.get(
                ENDPOINT, headers=HEADERS, params=current_timestamp
            )
            if response != response:
                homework = get_api_answer(current_timestamp)
                message = parse_status(homework)
                send_message(bot, message)
            else:
                None
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)
        else:
            None


if __name__ == '__main__':
    main()
