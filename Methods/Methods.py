import logging
import os
import random
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import pytz
import requests
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tzlocal import get_localzone

# Configure logging to log to both console and file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Create a file handler for logging
file_handler = logging.FileHandler('RunLog.txt', mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


def send_tg(message):
    tg_token = "%tg_token%"
    tg_chat_id = "%tg_chat_id%"
    message_content = message
    url_TG = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={message_content}"
    response = requests.get(url_TG)  # Send the HTTP GET request
    return response.status_code


def send_tg_ss(filename):
    tg_token = "%tg_token%"
    tg_chat_id = "%tg_chat_id%"
    url_TG_image = f"https://api.telegram.org/bot{tg_token}/sendPhoto?chat_id={tg_chat_id}"
    with open(filename, "rb") as image_file:
        files = {"photo": image_file}
        response = requests.post(url_TG_image, files=files)
        # Check the response
    if response.ok:
        print("Image sent successfully!")
    else:
        print("Failed to send image:", response.text)


def convert_to_local_time(self):
    # Get the local timezone
    local_tz = get_localzone()
    # Define the local timezone
    local_tz = pytz.timezone('Europe/Rome')
    # Get the current local time
    local_now = datetime.now(local_tz)
    # Convert local time to local time
    local_now = local_now.astimezone(local_tz)
    # Format the local time as desired
    local_time_str = local_now.strftime("%H:%M:%S")
    local_date_str = local_now.strftime("%d.%m.%y")
    return local_date_str, local_time_str


def log_txt(message):
    print(message + '\n')


def write_keys(element, text, delay=1):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)


def login_to_website(GDS, AL, FROM, TO, browser_driver, email, password):
    try:
        openSite_time = time.time()
        browser_driver.get('https://www.testingwebsite.com/')

        auth_Btn = WebDriverWait(browser_driver, 200).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Login into my profile")]')))
        auth_Btn.click()
        print("Test: Login into my profile...")
        time.sleep(2)

        loginInput = WebDriverWait(browser_driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="email"]')))
        loginInput.click()
        loginInput.send_keys(email)
        print("Test: email")
        time.sleep(1)

        passwordInput = WebDriverWait(browser_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        passwordInput.click()
        time.sleep(1)
        passwordInput.send_keys(password)
        print("Test: password")
        time.sleep(1)

        loginYellowButton = WebDriverWait(browser_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@automation-id="loginButton"]')))
        loginYellowButton.click()
        print("Test: loginButton")
        time.sleep(5)
        # time between actions
        end_openSite_time = time.time()
        openSiteFULL_time = end_openSite_time - openSite_time
        seconds = int(openSiteFULL_time)
        openSiteFULL_time_formatted = f"{seconds}s"
        print("Test: login_to_website end")
        WebDriverWait(browser_driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, '//button[@automation-id="loginButton"]')))
        print(f"Text does NOT exist on the screen.")

    except Exception as e:
        # Take a screenshot in case of error
        browser_driver.save_screenshot("Tests/Pay/ss/login_error_screenshot.png")
        time.sleep(4)

        # Use the convert_to_local_time function
        local_date_str, local_time_str = convert_to_local_time()

        # Send Telegram message with error
        send_tg(
            "$Test failed at stage:  User Login > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/login_error_screenshot.png")

        # Log the error details
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  User Login > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n")
        return False
    return openSiteFULL_time_formatted


def search_flight(GDS, AL, FROM, TO, browser_driver):
    try:
        print("Test: search_flight  time.sleep(5) end")
        input_whereFromSearchField = browser_driver.find_element(By.ID, 'whereFromSearchField')
        input_whereFromSearchField.click()

        time.sleep(1)
        write_keys(input_whereFromSearchField, FROM)
        time.sleep(1)

        city_elements = WebDriverWait(browser_driver, 100).until(EC.visibility_of_all_elements_located((By.XPATH,
                                                                                                        '//div[contains(@class, "cities_list")]/ul/li')))
        if len(city_elements) > 1:
            WebDriverWait(browser_driver, 100).until(EC.visibility_of_element_located(
                (By.XPATH, f'//span[contains(@class, "city_from") and text()="{FROM}"]')))

        pickFROM = browser_driver.find_element(By.XPATH,
                                               f"//span[contains(@class, 'city_from') and text()='{FROM}']")
        pickFROM.click()

        time.sleep(1)

        input_whereToSearchField = browser_driver.find_element(By.ID, 'whereToSearchField')
        input_whereToSearchField.click()

        time.sleep(1)
        write_keys(input_whereToSearchField, TO)
        time.sleep(1)

        city_elements_TO = WebDriverWait(browser_driver, 100).until(EC.visibility_of_all_elements_located((By.XPATH,
                                                                                                           '//div[contains(@class, "suggestion__SuggestionWrapper")]/ul/li')))
        if len(city_elements_TO) > 1:
            WebDriverWait(browser_driver, 100).until(EC.visibility_of_element_located(
                (By.XPATH, f'//span[contains(@class, "city_to") and text()="{TO}"]')))
        time.sleep(1)
        pickTO = browser_driver.find_element(By.XPATH,
                                             f"//span[contains(@class, 'city_to') and text()='{TO}']")
        pickTO.click()
        print("Test: whereToSearchField.pickTO.click()(TO)")
        time.sleep(1)

        # Choose flight day
        browser_driver.find_element(By.XPATH, "//label[contains(text(),'TO')]/ancestor::button").click()
        time.sleep(2)
        datePickerForwardButton = browser_driver.find_element(By.CSS_SELECTOR, 'div[automation-id="dateForwardButton"]')
        datePickerForwardButton.click()
        time.sleep(2)
        datePickerForwardButton.click()
        print("Test: TO dateForwardButton")
        time.sleep(3)

        # Pick random date of flight
        day_cells = browser_driver.find_elements(By.CSS_SELECTOR, '[automation-id="dayOfFlight"]')
        filtered_day_cells = [cell for cell in day_cells if int(cell.text) in range(1, 29)]
        random_day_cell = random.choice(filtered_day_cells)
        random_day_cell.click()
        time.sleep(2)
        datePickerForwardButton.click()
        time.sleep(2)
        random_day_cell2 = random.choice(filtered_day_cells)
        random_day_cell2.click()
        time.sleep(2)
        print("Test: TO random.choice(filtered_day_cells)")

        # Mark the time before clicking the submit button
        submit_button_click_time = time.time()

        submitBtn = browser_driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submitBtn.click()

        WebDriverWait(browser_driver, 150).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='search_result']")))
        print("presence_of_element_located.")
        WebDriverWait(browser_driver, 300).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='search_result']")))
        print("presence_of_element_not_located.")

        AL_in_filter = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "AirlineFilter")]'))
        )
        time.sleep(1)
        browser_driver.execute_script("arguments[0].scrollIntoView(true);", AL_in_filter)
        time.sleep(1)
        AL_in_filter.click()
        print("Airline FILTER")

        # time between actions
        end_time_FindTickets = time.time()
        time_taken_FindTickets = end_time_FindTickets - submit_button_click_time
        seconds = int(time_taken_FindTickets)
        time_taken_end_time_FindTickets_formatted = f"{seconds}s"

        return True, time_taken_end_time_FindTickets_formatted

    except Exception as e:
        # If an exception occurs, take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/search_flight_error_screenshot.png")
        time.sleep(4)
        # Use the convert_to_local_time function

        local_date_str, local_time_str = convert_to_local_time()

        send_tg(
            "$Test failed at stage:  search of flight > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/search_flight_error_screenshot.png")
        # Write the exception details to the file
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  search of flight > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n")
        return False


def select_AL_Ticket(GDS_CODE, GDS, A_L, AL, FROM, TO, browser_driver):
    try:
        time.sleep(1)
        print("select_AL_Ticket")

        # Get current url to extract order number 
        parsed_url_search = urlparse(browser_driver.current_url)
        pathsearch = parsed_url_search.path
        searchOpen_str_value = str(pathsearch)
        print(searchOpen_str_value)
        time.sleep(1)

        AL_in_filter_select = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "{A_L}")]')))
        print("FOUND: " + A_L + " in FILTER")
        time.sleep(2)

        AL_in_filter_select.click()
        print("Click in filter " + AL + " in FILTER")
        time.sleep(2)
        print(AL + "is found  in FILTER")

        print("Price button ")

        price_button = WebDriverWait(browser_driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//button[contains(text(), "Buy")]'))
        )
        time.sleep(4)
        # Extract the text from the button
        button_text = price_button.text
        # Extracting digits from the text
        price_digits = re.findall(r'\d', button_text)
        # Join the digits together to form the price
        price_text = ''.join(price_digits)
        # Convert the price to an integer
        priceInSearch = int(price_text)
        # Print the price
        print("Price before click: priceInSearch ", priceInSearch)
        # Click on the button
        time.sleep(2)
        buyAviaTicketButton_time = time.time()

        # Create an XPath expression that matches the button with the specified text and data-gds attribute
        xpath_expression = f'//button[contains(text(), "Buy") and @data-gds="{GDS_CODE}"]'

        # Wait until the button with the specified conditions is visible
        price_button_GDS = WebDriverWait(browser_driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, xpath_expression))
        )
        # Click the button
        price_button_GDS.click()
        time.sleep(2)

        flightDetail = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//span[contains(text(), "Flight details")]')))
        # time between actions
        booking_page_loaded_time = time.time()
        time_taken_OpenFlight = booking_page_loaded_time - buyAviaTicketButton_time
        seconds = int(time_taken_OpenFlight)
        time_taken_OpenFlight_formatted = f"{seconds}s"
        print(f"Time taken OpenFlight : {time_taken_OpenFlight_formatted}")

        print("Booking price")
        price_Booking = WebDriverWait(browser_driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//span[@automation-id="totalBookingPrice"]'))
        )
        browser_driver.execute_script("arguments[0].scrollIntoView(true);", price_Booking)
        time.sleep(7)
        # Extract the text from the button
        price_Booking_text = price_Booking.text
        # Extracting digits from the text
        price_Booking_digits = re.findall(r'\d', price_Booking_text)
        # Join the digits together to form the price
        price_Bookingtext = ''.join(price_Booking_digits)
        # Convert the price to an integer
        priceInBook = int(price_Bookingtext)
        # Print the price
        # Print the price
        print("Price booking: priceInBook ", priceInBook)

        return time_taken_OpenFlight_formatted, priceInSearch, priceInBook
    except Exception as e:
        # If an exception occurs, take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/Open_Flight_error_screenshot.png")
        time.sleep(4)
        # Get the local timezone
        local_date_str, local_time_str = convert_to_local_time()

        send_tg(
            "$Test failed at stage:  Open flight > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/Open_Flight_error_screenshot.png")
        # Write the exception details to the file
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  Open flight > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n\n")
        # browser_driver.quit()
        return False


def AddSeatRT(GDS, A_L, AL, FROM, TO, browser_driver):
    try:
        buttonAddSeat = WebDriverWait(browser_driver, 100).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[automation-id="addSeat"]')))
        buttonAddSeat.click()

        time.sleep(5.5)

        seat_element = WebDriverWait(browser_driver, 100).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            '//div[starts-with(@automation-id, "seatLowPrice") or starts-with(@automation-id, "seatRegularPrice") or starts-with(@automation-id, "seatHighPrice")]')))
        seat_element.click()

        print("seat piked\n")
        time.sleep(1)

        endPick = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[contains(text(), "Finish choosing seats")]')))
        endPick.click()

        print("endPick\n")
        time.sleep(5.5)

    except Exception as e:
        # If an exception occurs, take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/AddSeat_error_screenshot.png")
        time.sleep(4)

        # Get the local timezone
        local_date_str, local_time_str = convert_to_local_time()

        send_tg(
            "$Test failed at stage:  Add Seat > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/AddSeat_error_screenshot.png")
        # Write the exception details to the file
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  Add Seat > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n\n")
        return False
    return True


def addBaggage(browser_driver):
    # Define the expected text
    expected_text = "Don't forget to add baggage"

    # Wait until the text is present on the page
    WebDriverWait(browser_driver, 100).until(
        EC.text_to_be_present_in_element((By.XPATH, '//*[contains(text(), expected_text)]'), expected_text)
    )

    buttonaddBaggage = WebDriverWait(browser_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[automation-id="buttonaddBaggage"]'))
    )

    buttonaddBaggage.click()
    time.sleep(4)

    # Wait for all elements with the specified text to be present
    elements = WebDriverWait(browser_driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//span[contains(text(), "Baggage limit: ")]'))
    )

    # If there are elements found, click the first one
    if elements:
        first_element = elements[0]
        first_element.click()
    else:
        print("No elements found with the specified text.")
    time.sleep(1)

    endPick = WebDriverWait(browser_driver, 300).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[contains(text(), "Finish ")]')))
    endPick.click()
    print("endPick.click()")
    time.sleep(1)


def AddPassenger(GDS, A_L, AL, FROM, TO, browser_driver):
    try:
        print("Read passenger list")
        relative_path = 'PassengerList.txt'

        # Calculate the project root by going two levels up from this script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
        file_path = os.path.join(project_root, relative_path)

        print(f"Looking for file at: {file_path}")
        print(f"Current working directory: {os.getcwd()}")

        # Generate random passenger from list
        with open(file_path, 'r', encoding='utf-8') as PassengerListFile:
            lines = PassengerListFile.readlines()
            random_index_last_name = random.randint(0, len(lines) - 1)
            random_index_name = random.randint(0, len(lines) - 1)
            last_name = lines[random_index_last_name].split(', ')[0]
            name = lines[random_index_name].split(', ')[1]
        print(f"Randomly selected last name: {last_name}")
        print(f"Randomly selected name: {name}")

        # Fill passenger details
        print("Fill passenger details")
        lastNameInput = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//input[@automation-id="lastName"]')))
        time.sleep(1.5)
        browser_driver.execute_script("arguments[0].scrollIntoView(true);", lastNameInput)
        time.sleep(1.5)
        lastNameInput.send_keys(last_name)

        NameInput = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//input[@automation-id="Name"]')))
        NameInput.send_keys(name)

        # Fill random date of birth
        random_birth_year = random.randint(1970, 2003)
        random_birth_month = random.randint(1, 12)
        random_birth_day = random.randint(1, 28)
        random_date_of_birth = f'{random_birth_day:02d}.{random_birth_month:02d}.{random_birth_year}'

        date_of_birth_input = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//input[@placeholder="dd.mm.yyyy"]')))
        date_of_birth_input.click()
        time.sleep(1.5)
        date_of_birth_input.send_keys(random_date_of_birth)
        time.sleep(2)
        date_of_birth_close = WebDriverWait(browser_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Choose"]'))
        )
        date_of_birth_close.click()

        # Fill random passport number
        random_passport_number = random.randint(10 ** 10, 10 ** 11 - 1)
        passport_number_input = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//input[@automation-id="passportNum"]')))
        passport_number_input.click()
        time.sleep(1.5)
        # Enter the random passport number and send the Enter key
        passport_number_input.send_keys(str(random_passport_number) + Keys.ENTER)

        print(str(random_passport_number) + " \n")
        time.sleep(2)
        return True
    except Exception as e:
        # If an exception occurs, take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/AddPassenger_error_screenshot.png")
        time.sleep(4)

        # Get the local timezone
        local_date_str, local_time_str = convert_to_local_time()

        send_tg(
            "$Test failed at stage:  Adding passenger  > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/AddPassenger_error_screenshot.png")
        # Write the exception details to the file
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  Adding passenger  > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n\n")
        # browser_driver.quit()
        return False


def checkOrderPrice(browser_driver, order_number_value):
    order_url = f'https://www.testingwebsite.com/orders/{order_number_value}'
    browser_driver.get(order_url)

    # Extract the price from the button
    print("Price : ")
    time.sleep(3)
    price_After_Pay_el = WebDriverWait(browser_driver, 60).until(
        EC.visibility_of_element_located((By.XPATH, '//span[@automation-id="orderPrice"]'))
    )
    # Extract the text from the button
    price_After_Pay_text = price_After_Pay_el.text
    # Extracting digits from the text
    price_After_Pay_digits = re.findall(r'\d', price_After_Pay_text)
    # Join the digits together to form the price
    price_After_Pay_text = ''.join(price_After_Pay_digits)
    # Convert the price to an integer
    price_After_Pay_f = int(price_After_Pay_text)
    # Print the price
    print("Price pay:", price_After_Pay_f)
    return price_After_Pay_f


def ProceedForeignFlights(GDS, AL, A_L, FROM, TO, browser_driver):
    try:

        def click_if_present(xpath, timeout=2):
            try:
                element = WebDriverWait(browser_driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                element.click()
                time.sleep(1)  # Optional, for stability
                return True
            except TimeoutException:
                print(f"Element with xpath {xpath} not found within {timeout} seconds. Skipping click.")
                return False

        # Accept terms
        if click_if_present('//div[@name="offer"]'):
            print("div[@name=offer] clicked")

        # Accept health declaration terms if present
        if click_if_present('//div[@name="healthInsurance"]'):
            print("div[@name=healthInsurance] clicked")

        # Accept email terms
        if click_if_present('//div[@name="emailNotification"]'):
            print("div[@name=emailNotification] clicked")

        # Continue button
        nextBookBtn = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "Go to payment")]')))
        nextBookBtn.click()
        time.sleep(3.5)

        booking_page_Next_time = time.time()

        order_number_value = ''
        url = browser_driver.current_url
        match = re.search(r'\d+', url)
        if match:
            order_number_value = match.group(0)
            print('Order Number Value:', order_number_value)

        # time between actions
        payment_page_loaded_time = time.time()
        time_taken_OpenFlight = payment_page_loaded_time - booking_page_Next_time
        seconds = int(time_taken_OpenFlight)
        payment_page_loaded_time_formatted = f"{seconds}s"
        print(f"Time taken payment_page_loaded_time  : {payment_page_loaded_time_formatted}")
        time.sleep(8)
        # Extract the price from the button
        print("Price After Booking ")
        price_After_Booking = WebDriverWait(browser_driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//span[@automation-id="totalBookingPrice"]'))
        )
        time.sleep(3)
        browser_driver.execute_script("arguments[0].scrollIntoView(true);", price_After_Booking)
        # Extract the text from the button
        time.sleep(12)
        price_After_Booking_text = price_After_Booking.text
        # Extracting digits from the text
        price_After_Booking_digits = re.findall(r'\d', price_After_Booking_text)
        # Join the digits together to form the price
        price_After_Bookingtext = ''.join(price_After_Booking_digits)
        # Convert the price to an integer
        price_After_Book = int(price_After_Bookingtext)
        # Print the price
        time.sleep(3)
        browser_driver.save_screenshot("Tests/Pay/ss/price_After_Book_Foreign_.png")
        time.sleep(3)
        print("Price booking Foreign:", price_After_Book)

        send_tg_ss(r"Tests/Pay/ss/price_After_Book_Foreign_.png")

        return payment_page_loaded_time_formatted, order_number_value, price_After_Book
    except Exception as e:
        # If an exception occurs, take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/Booking_Flight_error_screenshot.png")
        time.sleep(4)
        # Get the local timezone
        local_date_str, local_time_str = convert_to_local_time()

        send_tg(
            "$Test failed at stage:  Flight Booking > " + GDS + " " + AL + " " + FROM + " - " + TO + "%0A" + local_date_str + " " + local_time_str)
        send_tg_ss(r"Tests/Pay/ss/Booking_Flight_error_screenshot.png")
        # Write the exception details to the file
        with open(r"Tests/Pay/testRunResults.txt", "a", encoding="utf-8") as file:
            file.write(
                "\n$Test failed at stage:  Flight Booking > " + GDS + " " + AL + " " + FROM + " - " + TO + "\n" + local_date_str + " " + local_time_str + "\n")
        # browser_driver.quit()
    return True


def AddServiceRefund(browser_driver):
    browser_driver.save_screenshot("Tests/Pay/ss/AAddServiceRefund.png")
    additionalServiceRefundButtonToggle = WebDriverWait(browser_driver, 300).until(
        EC.element_to_be_clickable((By.XPATH, f'//button[@automation-id="AddServiceRefund"]')))
    additionalServiceRefundButtonToggle.click()
    time.sleep(1)
    browser_driver.save_screenshot(
        "Tests/Pay/ss/AAddServiceRefund_ButtonToggle.click().png")
    time.sleep(12)
    return True


def AddFirstInsurance(browser_driver):
    browser_driver.save_screenshot("Tests/Pay/ss/AddFirstInsurance.png")
    insuranceChoiceButton_1 = WebDriverWait(browser_driver, 300).until(
        EC.element_to_be_clickable((By.XPATH, f'//button[@automation-id="AddFirstInsurance"]')))
    insuranceChoiceButton_1.click()
    time.sleep(1)
    browser_driver.save_screenshot(
        "Tests/Pay/ss/AddFirstInsurance_insuranceChoiceButton_1.click().png")
    time.sleep(12)
    return True


def cancelOrder(GDS, A_L, AL, FROM, TO, browser_driver):
    import re

    order_number_value = ''
    url = browser_driver.current_url
    match = re.search(r'\d+', url)
    if match:
        order_number_value = match.group(0)
        print('Order Number Value:', order_number_value)

        print(str(order_number_value) + "N booking\n")

    order_url = f'https://www.testingwebsite.com/orders/{order_number_value}'
    browser_driver.get(order_url)

    cancelButton = WebDriverWait(browser_driver, 300).until(
        EC.presence_of_element_located((By.XPATH, '//button[@automation-id="cancel"]')))
    cancelButton.click()
    time.sleep(1)
    try:
        checkCancel = WebDriverWait(browser_driver, 300).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Canceled")]')))

        # Send the message
        send_tg("Order " + order_number_value + " Canceled ✅")

    except:
        send_tg("$Order {order_number_value} Not in state  Canceled ❌ " + AL + " ; " + FROM + " - " + TO)
    return True


def payWithTestCard(browser_driver):
    # Pay order with test card and then make return of order
    import re

    order_number_value = ''
    url = browser_driver.current_url
    match = re.search(r'\d+', url)
    if match:
        order_number_value = match.group(0)
        print('Order Number Value:', order_number_value)

        print(str(order_number_value) + "N booking\n")

    order_url = f'https://www.testingwebsite.com/orders/{order_number_value}'
    browser_driver.get(order_url)
    # Wait for the desired step element to appear
    wait = WebDriverWait(browser_driver, 300)
    desired_step = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//*[contains(text(), 'You agreed to next terms:')]")))
    # Scroll to the desired step
    browser_driver.execute_script("arguments[0].scrollIntoView(true);", desired_step)

    wait = WebDriverWait(browser_driver, 300)
    russian_card_image = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//img[contains(@src, '/static/media/Card.123456.svg')]")))
    russian_card_image.click()

    wait = WebDriverWait(browser_driver, 300)
    iframe_element = wait.until(EC.presence_of_element_located((By.ID, "iFrame1")))
    # Switch to the iframe
    browser_driver.switch_to.frame(iframe_element)
    wait = WebDriverWait(browser_driver, 300)

    # Wait for the card input field to be visible
    card_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[automation-id='card_card']")))
    card_input.click()
    time.sleep(1)
    card_input.send_keys("4000000000000000")
    print("4000000000000000")
    time.sleep(1)

    # Wait for the card expiration input field to be visible
    card_input_expire = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[automation-id='card_expire']")))
    card_input_expire.send_keys("0000")
    time.sleep(1)

    # Wait for the card CVV input field to be visible
    card_input_CVV = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[automation-id='card_cvc']")))
    card_input_CVV.send_keys("000")
    time.sleep(5)

    # Wait for the payment button to be clickable
    button_pay = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[automation-id='card_submit']")))

    button_pay.click()

    # Switch back to the default content
    browser_driver.switch_to.default_content()

    # Navigate to the URL
    try:
        paymentCheck2 = WebDriverWait(browser_driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Paid")]')))
    except TimeoutException:
        send_tg("Order " + order_number_value + " is Not Paid")
    else:
        # Send the message
        order_url = f'https://www.testingwebsite.com/orders/{order_number_value}'
        browser_driver.get(order_url)

        price_After_Pay_el = WebDriverWait(browser_driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//span[@automation-id="orderPrice"]'))
        )
        time.sleep(5)
        # Extract the text from the button
        price_After_Pay_text = price_After_Pay_el.text
        # Extracting digits from the text
        price_After_Pay_digits = re.findall(r'\d', price_After_Pay_text)
        # Join the digits together to form the price
        price_After_Pay_text = ''.join(price_After_Pay_digits)
        # Convert the price to an integer
        price_After_Pay_f = int(price_After_Pay_text)
        # Print the price
        print("Price pay:", price_After_Pay_f)

        # Take a screenshot
        browser_driver.save_screenshot("Tests/Pay/ss/Paid.png")
        print('Payment status: Paid ', order_number_value)
        send_tg("Order " + order_number_value + " is Paid 💸")

    time.sleep(5)
    # returning of order to return money back
    print("START return " + order_number_value)
    print("Login Request:\n")

    # Perform login
    login_url = 'http://testingwebsite/api/sign-in'
    login_payload = {
        'grant_Type': 'password',
        'login': '%login%',
        'password': '%password%'
    }
    login_headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # Make login request
    print("return: LOGIN")
    login_response = requests.post(login_url, headers=login_headers, json=login_payload)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {timestamp}\n")
    print(f"Request URL: {login_url}\n")
    print(f"Request Body: {login_payload}\n")
    print(f"Response Status Code: {login_response.status_code}\n")

    try:
        response_json = login_response.json()
        print(f"Response Body: {response_json}\n\n")
    except ValueError:
        response_text = login_response.text
        print(f"Response Body: {response_text}\n\n")

    if login_response.status_code == 200:
        access_token = response_json.get('accessToken') if 'accessToken' in response_json else None

        # Get order
        print("return: GET ORDER")
        order_url = f'http://testingwebsite/api/Order/OrderNumber={order_number_value}'
        order_headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        # Make order request
        print("Order Request:\n")
        print(f"Request URL: {order_url}\n")
        print(f"Request Headers: {order_headers}\n")

        order_response = requests.get(order_url, headers=order_headers)
        print(f"Response Status Code: {order_response.status_code}\n")

        try:
            response_json = order_response.json()
            print(f"Response Body: {response_json}\n\n")
        except ValueError:
            response_text = order_response.text
            print(f"Response Body: {response_text}\n\n")

        if order_response.status_code == 200:
            order_locations_id = response_json.get('orderLocations')[0]['id']
            print(f"Order Positions ID: {order_locations_id}")

            # return order
            return_url = 'http://testingwebsite/api/order/return'
            return_payload = {
                'orderNumber': order_number_value,
                'orderLocationId': order_locations_id,
            }
            return_headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
            }
            basic_auth = ('login', 'pass')

            # Make return request
            print("return Request:\n")
            print(f"Request URL: {return_url}\n")
            print(f"Request Headers: {return_headers}\n")
            print(f"Request Body: {return_payload}\n")

            return_response = requests.delete(return_url, headers=return_headers, json=return_payload, auth=basic_auth)
            print(f"Response Status Code: {return_response.status_code}\n")

            response_json = return_response.json()
            print(f"Response Body: {response_json}\n\n")

            print("return:", order_number_value, "200 OK ✅")
            time.sleep(2)

            # Check return
            browser_driver.get(order_url)
            try:
                returnCheck = WebDriverWait(browser_driver, 100).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Returned")]')))
            except TimeoutException:
                send_tg("Order " + order_number_value + " Not in state Returned ❌")
            else:
                # Take a screenshot
                print("return:", order_number_value, "Returned ✅")
                browser_driver.save_screenshot("Tests/Pay/ss/Returned.png")
                send_tg("Order " + order_number_value + " Returned ✅")

    time.sleep(2)
    return order_number_value, price_After_Pay_f
