import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from bs4 import BeautifulSoup
import re
import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ACTION_CLICK = "click"
ACTION_GET_TEXT = "get_text"

# Словарь компаний с сокращенными и полными именами
# List of company entries
companies_entries = [
    "X5 Group - КОРПОРАТИВНЫЙ ЦЕНТР ИКС 5 9722079341",
    "Черкизово - Группа Черкизово 7718560636",
    "BIOCAD - БИОКАД 5024048000",
    "Hoff - ДОМАШНИЙ ИНТЕРЬЕР 7709770002",
    "Яндекс Райдтех - ЯНДЕКС.ТАКСИ 7704340310",
    "Крок - КРОК ИНКОРПОРЕЙТЕД 7701004101",
    "Nebius - МЕЖДУНАРОДНАЯ КОМПАНИЯ ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"ЯНДЕКС\" 3900019850",
    "Click2Money - КЛИК-ТУ-МАНИ 7704486319",
    "Pay365 - ПЭЙ 365 7709487010",
    "OZON - ОЗОН ПОВОЛЖЬЕ 6330094512",
    "РСХБ - РОССИЙСКИЙ СЕЛЬСКОХОЗЯЙСТВЕННЫЙ БАНК 7725114488",
    "Хеликон - КОМПАНИЯ ХЕЛИКОН 7704543951",
    "Cloud.ru - ОБЛАЧНЫЕ ТЕХНОЛОГИИ 7736279160",
    "Самолёт - ГРУППА КОМПАНИЙ \"САМОЛЕТ\" 9731004688",
    "Яндекс Маркет - МЕЖДУНАРОДНАЯ КОМПАНИЯ ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"ЯНДЕКС\" 3900019850",
    "Яндекс.Cloud - МЕЖДУНАРОДНАЯ КОМПАНИЯ ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"ЯНДЕКС\" 3900019850",
    "IVI - ИВИ.РУ 7723624187",
    "Banki.ru - ИНФОРМАЦИОННОЕ АГЕНТСТВО \"БАНКИ.РУ 7723527345",
    "585 RPO - РЕГЕНТ ГОЛД 7814566648",
    "Сбер Еаптека - ЕАПТЕКА 7704865540",
    "Информзащита - ИНФОРМЗАЩИТА 7702148410",
    "Onpoint - ОНПОИНТ 7710907340",
    "Food Rocket - РОКЕТ ФУД 7727457459",
    "Hawex",
    "Loymax - ЛОЙМАКС 7718818860",
    "EggHeads - ЭГГХЕДС 9731071733",
    "Брусника - БРУСНИКА 6671382990",
    "Amdocs - АМДОКС СОЛЮШНЗ ЛТД 7710393180",
    "ЮЛаки - ЮЛаки 9705198370",
    "Fun&Sun - ТТ-Трэвел 7714775020",
    "nil.foundation - ОБЪЕДИНЕННАЯ НАУЧНО-ИССЛЕДОВАТЕЛЬСКАЯ ЛАБОРАТОРИЯ СУДЕБНЫХ ЭКСПЕРТИЗ 7751152088",
    "Brand Analytics - БРЕНД АНАЛИТИКС 7842446470",
    "М.Видео – Эльдорадо - М.ВИДЕО 7707602010",
    "Equifax - БЮРО КРЕДИТНЫХ ИСТОРИЙ \"СКОРИНГ БЮРО 7708429953",
    "Mercury - МЕРКУРИЙ РИТЕЙЛ ХОЛДИНГ 9703127582",
    "МТС Банк (Аутсорс) - МТС-БАНК 7702045051",
    "МТС (Аутсорс) - ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"МОБИЛЬНЫЕ ТЕЛЕСИСТЕМЫ\" 7740000076",
    "Хантфлоу - Хантфлоу 9715317940",
    "Papa John's -  ПАПА ДЖОНС ЕКАТЕРИНБУРГ 3808214665",
    "Национальная Лотерея - НАЦИОНАЛЬНАЯ ЛОТЕРЕЯ 5043079910",
    "ЛитРес - ЛИТРЕС 7719571260",
    "InDrive - СОФТФОРМИНГ 1400009112",
    "Просвещение - ИЗДАТЕЛЬСТВО \"ПРОСВЕЩЕНИЕ\" 7715995942",
    "Совкомбанк - СОВКОМБАНК 4401116480",
    "Национальная Медиа Группа (МСБ) - НАЦИОНАЛЬНАЯ МЕДИА ГРУППА 7704676655",
    "ЦБ РФ -  ЦЕНТРАЛЬНЫЙ БАНК РОССИЙСКОЙ ФЕДЕРАЦИИ  7702235133",
    "SRG Group - ЭСАРДЖИ-КОНСАЛТИНГ 2221034139",
    "Этнамед - ЭТНАМЕД 7726747596",
    "Usetech - ЮЗТЕХ770703327902",
    "Яндекс. Такси - ЯНДЕКС.ТАКСИ 7704340310",
    "АО Азот-Взрыв - АЗОТ-ВЗРЫВ 7727218041",
    "Glue up",
    "PIM Solutions - ПОМОЩЬ ИНТЕРНЕТ-МАГАЗИНАМ 7702824562",
    "Metaship - МЕТАШИП-МОСКВА 7702392344",
    "Sitronics - СИТРОНИКС 7735116621",
    "4 Лапы - ЧЕТЫРЕ ЛАПЫ - ИМ 5040172478",
    "Ингосстрах - ИНГОССТРАХ 7705042179",
    "Nestle -  НЕСТЛЕ РОССИЯ 7705739450",
    "Auxo - АУКСО ИТ СЕРВИСЕЗ 9726035391",
    "Айтуби - АЙТУБИ 7729663658",
    "Sunlight - СОЛНЕЧНЫЙ СВЕТ 7731316845",
    "Air Liquide - ЭР ЛИКИД 7709606250",
    "Т2 - Т2 МОБАЙЛ 7743895280",
    "Яндекс Академия - ОБРАЗОВАТЕЛЬНЫЕ ТЕХНОЛОГИИ ЯНДЕКСА 7704282033"
]

# Create the dictionary
companies_dict = {}

for entry in company_entries:
    if " - " in entry:
        key, value = entry.split(" - ", 1)
        companies_dict[key.strip()] = value.strip()
    else:
        companies_dict[entry.strip()] = None

# Функция для запуска браузера
def run_browser(results_event, results_container):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service("C:/Users/Zver/Downloads/chromedriver-win64/chromedriver.exe")  # Укажите путь к chromedriver

    driver = webdriver.Chrome(service=service, options=options)
    try:
        def search_company(name: str):
            logger.info(f"Поиск компании: {name}")
            # Находим поле ввода поиска
            search_field = driver.find_element(By.ID, "autocomplete-0-input")
            search_field.send_keys(name)
            search_field.send_keys(Keys.ENTER)

            # Ждём загрузки результатов
            time.sleep(3)
            logger.info(f"Результаты поиска для компании {name} загружены")

        def interact_with_element_by_xpath(xpath, action=ACTION_CLICK):
            try:
                wait = WebDriverWait(driver, 10)
                elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))

                if elements:
                    if action == ACTION_CLICK:
                        elements[0].click()
                        logger.info(f"Элемент по XPath {xpath} успешно нажат")
                    elif action == ACTION_GET_TEXT:
                        text = elements[0].text
                        return text
                else:
                    logger.warning(f"Элементы по XPath {xpath} не найдены")
                    return "Не найдено"
            except NoSuchElementException as e:
                logger.error(f"Ошибка: Элемент по XPath {xpath} не найден - {e}")
                return "Не найдено"
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                return "Не найдено"

        # Открываем сайт
        driver.get("https://zachestnyibiznes.ru")
        logger.info("Сайт успешно открыт")

        results = []

        for short_name, full_name in companies_dict.items():
            try:
                search_company(full_name)
                interact_with_element_by_xpath('//*[@id="search_result"]/div[2]/div/div/p[1]/a', ACTION_CLICK)
                workers_count = interact_with_element_by_xpath('//*[@id="right-data-company"]/div/div[1]/div[4]/div/div[2]/div[6]/div[1]/div[2]/span', ACTION_GET_TEXT)
                logger.info(f"Число сотрудников для компании {full_name}: {workers_count}")

                profit = "Не найдено"
                benefit = "Не найдено"
                try:
                    logger.info("Поиск второго дива с классами 'nav-tab-pane nav-tab-active-pane'")
                    div_elements = driver.find_elements(By.CLASS_NAME, "nav-tab-pane.nav-tab-active-pane")
                    if len(div_elements) < 2:
                        raise NoSuchElementException("Не найдено достаточно элементов с классами 'nav-tab-pane nav-tab-active-pane'")
                    second_div = div_elements[1]
                    logger.info("Второй див найден")

                    logger.info("Извлечение id из второго дива")
                    div_id = second_div.get_attribute("id")
                    logger.info(f"ID извлечен: {div_id}")

                    logger.info("Поиск элемента по XPath с использованием извлеченного id")
                    xpath_expression = f"//*[@id='{div_id}']/div[1]/div[2]/div[2]/div[2]/p/a"
                    target_element = driver.find_element(By.XPATH, xpath_expression)
                    logger.info("Элемент найден")

                    logger.info("Получение текста из элемента")
                    profit = target_element.text
                    logger.info(f"Текст получен: {profit}")

                    logger.info("Поиск элемента по XPath с использованием извлеченного id")
                    xpath_expression = f"//*[@id='{div_id}']/div[1]/div[2]/div[1]/div[2]/p/a"
                    target_element = driver.find_element(By.XPATH, xpath_expression)
                    logger.info("Элемент найден")

                    logger.info("Получение текста из элемента")
                    benefit = target_element.text
                    logger.info(f"Текст получен: {benefit}")

                except NoSuchElementException as e:
                    logger.error(f"Ошибка: Элемент не найден - {e}")

                # Извлечение следующего слова после фразы "Полный отчет по"
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text()
                match = re.search(r'Полный отчет по\s+(\S+)', text_content)
                next_word = match.group(1) if match else "Не найдено"
                logger.info(f"Следующее слово после 'Полный отчет по': {next_word}")

                results.append({
                    "short_name": short_name,
                    "full_name": full_name,
                    "workers_count": workers_count,
                    "profit": profit,
                    "benefit": benefit,
                    "next_word_after_full_report": next_word
                })

            except Exception as e:
                logger.error(f"Произошла ошибка при обработке компании {full_name}: {repr(e)}")

        for result in results:
            logger.info(f"Результат для компании {result['full_name']}:")
            logger.info(f"Число сотрудников: {result['workers_count']}")
            logger.info(f"Прибыль: {result['profit']}")
            logger.info(f"Доход: {result['benefit']}")
            logger.info(f"Следующее слово после 'Полный отчет по': {result['next_word_after_full_report']}")

        # Сохраняем результаты и устанавливаем событие
        results_container.extend(results)
        results_event.set()

    except Exception as e:
        logger.error(f"Произошла ошибка: {repr(e)}")

    finally:
        # Закрыть браузер после завершения
        driver.quit()
        logger.info("Браузер закрыт")

# Создаём событие и контейнер для результатов
results_event = threading.Event()
results_container = []

# Создаём новый поток для запуска браузера
browser_thread = threading.Thread(target=run_browser, args=(results_event, results_container))
browser_thread.start()

# Здесь можно делать другие операции параллельно с браузером
logger.info("Браузер запущен, продолжаем выполнять другие задачи...")

# Дожидаемся завершения потока браузера
browser_thread.join()
logger.info("Задача с браузером завершена.")

df = pd.DataFrame(results_container)
df