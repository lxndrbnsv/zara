import string
import random
import traceback
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)

import config as cfg
from utils import WriteProductsJson


def get_current_time():
    return datetime.datetime.now()


class GetProductLinks:
    """Из-за StaleElementReferenceException, появляющегося по непонятным
    причинам после загрузки каждой следуюший странички, приходится выполнять
    перезапуск браузера."""

    def __init__(self, category):
        def close_popups():
            to_close = browser.find_elements_by_class_name("modal__close-icon")
            for i in to_close:
                try:
                    i.click()
                except StaleElementReferenceException:
                    pass
                except ElementClickInterceptedException:
                    pass
                except ElementNotInteractableException:
                    pass

        def close_cookies_banner():
            cookies_banner = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )

            try:
                cookies_banner.click()
            except TimeoutException:
                pass

        def get_links():
            def scroll_to_last_product(product):
                print(f"{get_current_time()} Scrolling...", flush=True)
                action.move_to_element(product).perform()

            product_links = []

            while True:
                len_in_beginning = len(product_links)

                product_link_tags = WebDriverWait(browser, 10).until(
                    ec.presence_of_all_elements_located((By.CLASS_NAME, "product-link"))
                )

                scroll_to_last_product(product_link_tags[-1])

                for product_link_tag in product_link_tags:
                    try:
                        cat_url = product_link_tag.get_attribute("href")
                        if cat_url not in product_links:
                            product_links.append(cat_url)
                    except NoSuchElementException as no_element:
                        print(no_element, flush=True)
                        pass
                current_len = len(product_links)

                if len_in_beginning == current_len:
                    print(
                        f"{get_current_time()} "
                        f"{str(current_len)} products have been collected.",
                        flush=True,
                    )
                    break

            return product_links

        options = Options()
        options.add_argument(f"--user-agent={cfg.request_data['user_agent']}")
        options.headless = True
        browser = webdriver.Chrome(
            executable_path=cfg.webdriver["path"], options=options
        )
        action = ActionChains(browser)
        browser.set_window_size("1366", "768")

        category_url = category["cat"]
        print(
            f"{get_current_time()} Collecting products in category: {category_url}",
            flush=True,
        )
        product_dicts = []
        try:
            browser.get(category_url)

            close_cookies_banner()
            close_popups()

            links = get_links()

            browser.quit()

            product_dicts = []

            for link in links:
                product_dicts.append(
                    dict(
                        product_link=link,
                        cat_url=category_url,
                        cat_id=category["cat_id"],
                    )
                )

            WriteProductsJson(product_dicts)
            print(f"{get_current_time()} Written.", flush=True)
            print("--- --- ---", flush=True)
        except WebDriverException as webdriver_exception:
            print(webdriver_exception)

        self.dicts = product_dicts


class GetProductData:
    def __init__(self, product):
        def close_popups():
            to_close = browser.find_elements_by_class_name("modal__close-icon")
            for i in to_close:
                try:
                    i.click()
                except StaleElementReferenceException:
                    pass
                except ElementClickInterceptedException:
                    pass
                except ElementNotInteractableException:
                    pass

        def close_cookies_banner():
            cookies_banner = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )

            try:
                cookies_banner.click()
            except TimeoutException:
                pass

        def colors():
            clrs = []

            color_selector_div = browser.find_element_by_class_name(
                "product-detail-color-selector__colors"
            )

            color_selectors = color_selector_div.find_elements_by_tag_name("li")
            for color_selector in color_selectors:
                clrs.append(color_selector)

            return clrs

        def multiple_colors():
            try:
                browser.find_element_by_class_name("product-detail-info__color")
                return False
            except NoSuchElementException:
                return True

        def get_current_color():
            color_tag = browser.find_element_by_class_name("product-detail-info__color")
            return color_tag.text.split(" | ", 1)[0].replace("Colour:", "").strip()

        def get_selected_color():
            color_tag = browser.find_element_by_class_name(
                "product-detail-color-selector__selected-color-name"
            )
            return color_tag.text.split(" | ", 1)[0].replace("Colour:", "").strip()

        def generate_product_ref():
            def generate():
                digits = string.digits
                try:
                    with open("./ref_codes.txt", "r") as txt_file:
                        text_data = txt_file.readlines()

                    existing_codes = []
                    for t in text_data:
                        existing_codes.append(t.replace("\n", ""))
                except FileNotFoundError:
                    existing_codes = []

                char_num = 1
                ref_code = "".join(random.choice(digits) for __ in range(char_num))
                while ref_code in existing_codes:
                    char_num = char_num + 1
                    ref_code = "".join(random.choice(digits) for __ in range(char_num))

                return int(ref_code)

            value = generate()
            with open("./ref_codes.txt", "a+") as text_file:
                text_file.write(f"{value}\n")

            return value

        def get_art():
            color_tag = browser.find_element_by_class_name("product-detail-info__color")
            return color_tag.text.split(" | ", 1)[1].strip()

        def get_selected_art():
            color_tag = browser.find_element_by_class_name(
                "product-detail-color-selector__selected-color-name"
            )
            return color_tag.text.split(" | ", 1)[1].strip()

        def get_name():
            return browser.find_element_by_tag_name("h1").text

        def get_pictures():
            imgs = []
            images_div = browser.find_element_by_class_name(
                "product-detail-view__images"
            )
            for picture_tag in images_div.find_elements_by_tag_name("picture"):
                if picture_tag.get_attribute("class") == "media-image":
                    source_tag = picture_tag.find_element_by_tag_name("source")
                    pics_list = source_tag.get_attribute("srcset").split(", ")
                    the_biggest_one = pics_list[-1].split(" ", 1)[0].strip()
                    if "contents" not in the_biggest_one:
                        imgs.append(the_biggest_one)

            return imgs

        def get_description():
            description_div = browser.find_element_by_class_name(
                "product-detail-description"
            )
            return description_div.find_element_by_tag_name("p").text

        def get_sizes():
            sizes_spans = browser.find_elements_by_class_name(
                "product-size-info__main-label"
            )
            sizes_data = []

            for sizes_span in sizes_spans:
                sizes_data.append(sizes_span.text)

            if len(sizes_data) > 0:
                return ", ".join(sizes_data)
            else:
                return None

        def get_price():
            price_span = browser.find_element_by_class_name("price__amount")
            return price_span.text.split(" ", 1)[0]

        def get_materials():
            show_materials_buttons = browser.find_elements_by_class_name(
                "product-detail-actions__action-button"
            )

            for button in show_materials_buttons:
                if button.text == "Source, materials & care":
                    button.click()
                    break

            materials_data = []

            mats = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, "product-detail-side-info-section__material-part")
                )
            )

            for mat in mats:
                materials_data.append(mat.text)

            close_popups()

            return ", ".join(materials_data)

        options = Options()
        options.add_argument(f"--user-agent={cfg.request_data['user_agent']}")
        options.headless = True
        browser = webdriver.Chrome(
            executable_path=cfg.webdriver["path"], options=options
        )
        browser.set_window_size("1920", "1080")

        url = product["product_link"]
        cat = product["cat_id"]
        print(f"{get_current_time()} Collecting data from {url}", flush=True)
        browser.get(url)

        results = []

        try:
            close_cookies_banner()
            close_popups()

            if multiple_colors() is False:
                print("Single!")
                current_color = get_current_color()
                ref = generate_product_ref()
                name = get_name()
                art = get_art()
                sizes = get_sizes()
                price = get_price()
                description = get_description()
                materials = get_materials()
                pictures = get_pictures()

                results_dict = dict(
                    cat_id=cat,
                    ref=ref,
                    color=current_color,
                    name=name,
                    art=art,
                    pictures=pictures,
                    description=description,
                    sizes=sizes,
                    materials=materials,
                    price=price,
                )

                results.append(results_dict)
            else:
                print("Multiple!")
                colors_list = colors()
                for clr in colors_list:
                    clr.click()

                    current_color = get_selected_color()
                    ref = generate_product_ref()
                    name = get_name()
                    art = get_selected_art()
                    sizes = get_sizes()
                    price = get_price()
                    description = get_description()
                    materials = get_materials()
                    pictures = get_pictures()

                    results_dict = dict(
                        cat_id=cat,
                        ref=ref,
                        color=current_color,
                        name=name,
                        art=art,
                        pictures=pictures,
                        description=description,
                        sizes=sizes,
                        materials=materials,
                        price=price,
                    )

                    results.append(results_dict)

        except WebDriverException as webdriver_exception:
            traceback.print_exc()
            print(get_current_time(), webdriver_exception, flush=True)
        except Exception as e:
            print(e)

        browser.quit()
        print(f"{get_current_time()} Product data has been collected!", flush=True)
        print("--- --- ---", flush=True)
        self.results = results
