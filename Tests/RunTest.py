import pytest
from selenium import webdriver

from Methods.Methods import send_tg, login_to_website, search_flight, select_AL_Ticket, AddPassenger, \
    AddFirstInsurance, cancelOrder, ProceedForeignFlights, convert_to_local_time


@pytest.fixture(scope="function")
def browser_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def test_1(browser_driver):
    print("Test 1: Starting...")
    TO = "%DESTINATION%"
    FROM = "%DEPARTURE%"
    A_L = "%Airline_Name%"
    AL = "%Airline_Name%"
    GDS = "%GDS%"
    GDS_CODE = "%GDS_CODE%"

    try:
        openSiteFULL_time_formatted = login_to_website(GDS, AL, FROM, TO, browser_driver, "%user_email%",
                                                       "%password%")
        assert openSiteFULL_time_formatted, "Failed at login_to_website"

        time_taken_end_time_FindTickets_formatted = search_flight(GDS, AL, FROM, TO, browser_driver)
        assert time_taken_end_time_FindTickets_formatted, "Failed at search_flight"

        parsed_time_FindTickets = time_taken_end_time_FindTickets_formatted[1]

        result = select_AL_Ticket(GDS_CODE, GDS, A_L, AL, FROM, TO, browser_driver)
        assert result, "Failed at select_AL_Ticket"
        time_taken_OpenFlight_formatted, priceInSearch, priceInBook = result

        assert AddPassenger(GDS, A_L, AL, FROM, TO, browser_driver), "Failed at AddPassenger"

        payment_page_loaded_time_formatted, order_number_value, price_After_Book = ProceedForeignFlights(GDS, AL, FROM,
                                                                                                         TO,
                                                                                                         browser_driver)
        assert payment_page_loaded_time_formatted, "Failed at ProceedForeignFlights"

        assert AddFirstInsurance(browser_driver), "Failed at AddFirstInsurance"

        assert cancelOrder(GDS, A_L, AL, FROM, TO, browser_driver), "Failed at cancelOrder"

        local_date_str, local_time_str = convert_to_local_time()
        message = ("*Airline > " + str(GDS) + " " + str(AL) + " " + FROM + " - " + TO + "%0A" +
                   "Order number: " + str(order_number_value) + "%0A" + "%0A" +
                   "Time between actions: " + "%0A" +
                   "Open site: " + str(openSiteFULL_time_formatted) + "%0A" +
                   "Search ticket and result list: " + str(parsed_time_FindTickets) + "%0A" +
                   "Buy ticket and open book screen: " + str(time_taken_OpenFlight_formatted) + "%0A" +
                   "Proceed booking and show ticket info screen: " + str(payment_page_loaded_time_formatted) + "%0A"
                   + "Price of ticket on search result list: " + str(priceInSearch)
                   + "%0A" + "Price of ticket on Booking screen: " + str(priceInBook)
                   + "%0A" + "Price of ticket after booking complete: " + str(price_After_Book) + "%0A"
                   + "%0A" + local_date_str + " " + local_time_str)
        send_tg(message)

        # Write the message to a file
        messageTXT = message.replace("%0A", "\n")
        with open("Tests/Pay/testRunResults.txt", "a", encoding='utf-8') as file:
            file.write(messageTXT + "\n\n")

    except Exception as e:
        print(e)
        assert False, str(e)
    finally:
        browser_driver.quit()
        print("Test 1: End...")

    assert True


if __name__ == "__main__":
    pytest.main(['-v', __file__])
