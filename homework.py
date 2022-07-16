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


HOMEWORK_VERDICTS = {
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
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except Exception:
        raise
    else:
        logger.info('Удачная отправка ообщения в Telegram')


def get_api_answer(current_timestamp):
    """Вовзвращает ответ API с типом данных Python."""
    timestamp = current_timestamp or int(time.time())
    request_params = {
        'url': 'https://practicum.yandex.ru/api/user_api/homework_statuses/',
        'headers': {
            'Authorization': f'OAuth {PRACTICUM_TOKEN}'
        },
        'params': {
            'from_date': timestamp
        }
    }
    logger.debug('Запрос к адресу' + request_params['url'] + 'запущен')
    try:
        response = requests.get(**request_params)
        if response.status_code != 200:
            raise OSError('При запросе к адресу ' + request_params['url']
                          + 'с параметром: ' + request_params['params']
                          + ', статус код не возвращает 200')
        response = response.json()
    except Exception:
        raise
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.debug('Начата проверка ответа API на корректность')
    if type(response['homeworks']) != list:
        raise TypeError('Тип данных homeworks - не лист')
    if 'homeworks' not in response:
        logger.error('Ответ API не содержит ключ homeworks')
        raise KeyError('В словаре нет homeworks')
    try:
        len(response['homeworks']) != 0
        return response['homeworks'][0]
    except Exception:
        logger.error('Список homeworks пустой')
        return response['homeworks']


def parse_status(homework):
    """Возвращает подготовленную для отправки в Telegram строку."""
    try:
        homework_name = homework.get('homework_name')
    except Exception:
        message = 'Домашняя работа с таким названием отсутствует в ответе API'
        logger.error(message)
        raise KeyError(message)
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_VERDICTS.keys():
        verdict = HOMEWORK_VERDICTS[homework_status]
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
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1634074965
    if check_tokens() is not True:
        raise SystemExit('Программа принудительно остановлена'
                         'из-за отсутствия переменных окружения')
    prev_report = {}
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homeworks = check_response(response)
            try:
                message = parse_status(homeworks)
                current_report = {
                    'name': homeworks.get('homework_name'),
                    'message': message,
                }
            except Exception:
                logging.error('Cбой при формировании сообщения в Telegram')
            if current_report != prev_report:
                try:
                    send_message(bot, message)
                    prev_report = current_report.copy()
                except Exception:
                    logging.error('Cбой при отправке сообщения в Telegram')
            else:
                logger.info('Нет новых статусов')
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)
        else:
            None


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(msg)s'
        ' - %(message)s',
        level=logging.DEBUG
    )
    main()
