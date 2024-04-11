"""
-----------------------------------------------------------------------------------------------------------------------
Example use of crawler code to scrape all categories from an arbitrary website that uses dynamic dropdown listboxes
to display the categories and contains a redirect "Go" button that only redirects to the selected category if clicked.
This particular website contains a primary dropdown listbox for the categories and subcategories and a secondary 
dropdown listbox for regions.

Remember to download and upgrade all necessary requirements.
Edit code to fit your own website. Remember to replace the base_url with your own website URL and all the xpaths
with the relevant xpaths of your desired elements to be crawled.

Author: Catherine Di, catherine_di_2004@outlook.com
-----------------------------------------------------------------------------------------------------------------------
"""

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException,\
    NoSuchElementException, NoSuchAttributeException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def init_browser():

    print("Loading Chrome ...")

    service = webdriver.ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # test first -> then uncomment to run in headless mode
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")  # disable images to speed up
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # suppress certain ChromeDriver log messages
    options.add_argument("--ignore-certificate-errors")  # ignore certificate errors
    options.add_argument("--disable-notifications")
    options.add_argument("--log-level=3")

    return webdriver.Chrome(service=service, options=options)

def wait_clickable(driver, xpath, timeout=10, click=False):
    # click an element - the correct approach with selenium

    ec = EC.element_to_be_clickable((By.XPATH, xpath))
    try:    # wait for the element to be clickable
        element = WebDriverWait(driver, timeout=timeout).until(ec)
    except TimeoutException:
        return None

    if not click:
        return element

    # use JavaScript to make the click
    # this works even when the element is not visiable
    # simply use element.click() doesn't work if the element is not visible
    driver.execute_script("arguments[0].click();", element)

    return element

def wait_all_elements(driver, xpath, timeout=10):
    # wait for all elements under the parent xpath to be present after reload

    ec = EC.presence_of_all_elements_located((By.XPATH, xpath)) # wait for all elements to be present
    try:
        WebDriverWait(driver, timeout=timeout).until(ec)
    except TimeoutException:
        return False

    return True

def page_load_complete(driver, timeout=10):
    # test if the page is fully loaded
    # not needed if you don't need the entire page to be loaded

    try:
        WebDriverWait(driver, timeout=timeout).until(
            # wait for the page to be completely loaded
            lambda driver: driver.execute_script("return document.readyState") == "complete")
    except TimeoutException:
        return False

    return True

def get_text_list(driver, xpathx, attribute=None):
    # get text of all the list items located by the xpath template xpathx
    # optional one single attribute value to return together
    # each item of the returned list has the format of element_text:attribute_value

    text_list = []
    i = 1
    while i > 0:
        xp = xpathx.replace("{#}", f"{i}")  # loop through the xpaths of all elements in the dropdown list
        try:
            element = driver.find_element(By.XPATH, xp)
        except NoSuchElementException:      # no more elements; exit the loop
            break
        try:
            text = element.text
        except StaleElementReferenceException:
            # re-locate the element
            element = wait_clickable(driver, xp)  # wait for the element to be clickable
            if element is None:
                break
            text = element.text
        if attribute is not None:
            av = ""
            try:
                av = element.get_attribute(attribute)
            except NoSuchAttributeException:
                pass
            text += ":" + av
        text_list.append(text)
        i += 1
    #

    return text_list

def scrape_all_categories():

    base_url = "https://some_website.com"   # start url of the website you want to crawl -> replace with your own url

    driver = init_browser()     # start the chrome browser
    driver.get(base_url)        # navigate to the base_url
    page_load_complete(driver) # wait for the page to be fully loaded

    # dismiss the cookie inquiry dialog box immediately
    reject_cookie_xpath = '//*[@id="onetrust-reject-all-handler"]'
    ec = EC.element_to_be_clickable((By.XPATH, reject_cookie_xpath))
    try:
        reject_button = WebDriverWait(driver, 10).until(ec)
        reject_button.click()
    except TimeoutException:
        print("Warning: cannot find the Cookie Inquiry Dialog Box!")

    # the region dropdown listbox (secondary listbox)
    rbox_xpath = '//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[2]/div/button'
    # the category dropdown listbox (primary listbox)
    cbox_xpath = '//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[1]/div/button'
    # the redirect button which triggers the reload of the domain listbox - e.g. a "Go" button next to the dropdown list
    # delete related code if your website does not have a redirect button
    redirect_xpath = '//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/button'
    # the domain table
    dbox_xpath = '//*[@id="app"]/div/main/div/div/section[2]/div/div/div[1]/table/tbody'

    if wait_clickable(driver, rbox_xpath, click=True) is None:
        print("# Error: can not find the Region Listbox!")
        return

    # the template xpath of for the secondary list items
    ritem_xpathx = '//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[2]/div/div/button[{#}]'
    region_list = get_text_list(driver, ritem_xpathx)

    region_list[0] = ""   # region string for the first item
    print(f"Find total {len(region_list)} regions")
    print(region_list)

    if wait_clickable(driver, cbox_xpath, click=True) is None:
        print("# Error: can not find the Category Listbox!")
        return

    # the template xpath of the primary list items
    citem_xpathx = '//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[1]/div/div/button[{#}]'
    # get text and attribute("class") value of each item of the listbox
    ta_list = get_text_list(driver, citem_xpathx, attribute="class")

    # extract the category and subcategory (if any) strings from the list items
    category_list = []
    cat_name = None       # the category name, initially None
    for ta in ta_list:
        [text, av] = ta.split(":")          # extract text and attribute value
        if av.find("subcategory") > 0:
            category = cat_name + "/" + text.lower()   # text contains the subcategory
        else:
            if cat_name is None:
                cat_name = ""                   # category string for the first item
            else:
                cat_name = text.lower()         # text contains the category
            category = cat_name
        category = category.replace(" - other", "").replace("&", "and").replace(" ", "-")
        category_list.append(category)          # categoary = the final category string
    #

    print(f"Find total {len(category_list)} categories")
    print(category_list)

    # first test the redirect button’s existance
    # remove if no redirect button on your website
    if wait_clickable(driver, redirect_xpath) is None:
        print("# Error: can not find the redirect button!")
        return

    all_data = {}   # the scraped data goes here {region : {category : domain_list}}

    # for each region and category combination, scrape the dynamically loaded domain list:
    # delete the outer loop if your website does not have a secondary dropdown list
    for i, region in enumerate(region_list[:10], start=1):   # limit to the first 10 region for testing -> remove the [:10] to scrape all region
        region_data = all_data.setdefault(region, {})
        # click the region dropdown listbox
        if wait_clickable(driver, rbox_xpath, click=True) is None:
            print("# Error: can not find the Region Listbox!")
            continue
        ritem_xpath = f'//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[2]/div/div/button[{i}]'
        # wait for the dynamically loaded list item to be clickable, then click it to make the selection
        if wait_clickable(driver, ritem_xpath, click=True) is None:
            continue
        for j, cat in enumerate(category_list[:10], start=1):  # limit to the first 10 categories for testing -> remove the [:10] to scrape all categories
            domain_list = region_data.setdefault(cat, [])
            print(f"\nScraping region[{i}] = {region}, cat[{j}] = {cat} ...")  # print the region and category
            # wait for the category dropdown listbox to be clickable; then click
            if wait_clickable(driver, cbox_xpath, click=True) is None:
                print("# Error: can not find the Category Listbox!")
                continue
            citem_xpath = f'//*[@id="app"]/div/main/div/div/section[1]/div/div/div[1]/div/div[1]/div/div/button[{j}]'
            # wait for the specific category or subcategory to be clickable; then click
            if wait_clickable(driver, citem_xpath, click=True) is None:
                continue
            # wait for the redirect button to be clickable; then click
            # remove code if no redirect button on your website
            if wait_clickable(driver, redirect_xpath, click=True) is None:
                print("# Error: could not find the redirect button!")
                continue
            # checks if the redirection wait time exceeded the limit by checking if the element is clickable again
            if wait_clickable(driver, redirect_xpath) is None:
                print("# Error: too slow to refresh the page!")
                continue
            # checks if the domain table is loaded on the new page
            if not wait_all_elements(driver, dbox_xpath):
                print("# Error: too slow to load the domain table!")
                continue
            time.sleep(2.0)   # wait for the table to be refreshed
            print(driver.current_url)
            # the template xpath of the list items
            ditem_xpathx = '//*[@id="app"]/div/main/div/div/section[2]/div/div/div[1]/table/tbody/tr[{#}]/td[2]/a/span[2]'
            domain_list += get_text_list(driver, ditem_xpathx)
            print(domain_list)
            driver.delete_all_cookies()     # delete cookies to disable the site's anti-scraping - important!

    driver.quit()   # close the browser

    return all_data

if __name__ == "__main__":

    all_data = scrape_all_categories()

    # write the scraped data to an excel file
    fname = "YOUR_FILE_NAME.txt"
    with open(fname, mode="w", encoding="utf-8") as f:
        print(all_data, file=f)

    print("Done scraping!")
