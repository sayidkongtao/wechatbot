# coding=utf-8
import sys
import numpy as np
import cv2
from appium import webdriver
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from openpyxl import load_workbook
reload(sys)
sys.setdefaultencoding('utf8')

PATH = lambda path: os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        path
    )
)


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def match_image(source_path, template_path, method=cv2.TM_CCOEFF_NORMED):
        source = cv2.imread(source_path)
        template = cv2.imread(template_path, 0)
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(source_gray, template, method)
        w, h = template.shape[::-1]

        threshold = 0.8
        loc = np.where(result >= threshold)

        final_location = []

        for pt in zip(*loc[::-1]):
            # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
            final_location.append({"x": pt[0], "y": pt[1], "width": w, "height": h})

        return final_location

    @staticmethod
    def load_data_from_excel(file_name):
        wb = load_workbook(file_name)
        work_sheet = wb[wb.sheetnames[0]]
        test_data = []
        for row in work_sheet.values:
            test_data.append(CaseDataModel(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return test_data


class MobileFunction:

    def __init__(self, driver):
        self.driver = driver
        self.webdriver_wait = WebDriverWait(self.driver, 30)

    @staticmethod
    def click(element):
        element.click()

    @staticmethod
    def send_text(element, value):
        element.send_keys(value)

    @staticmethod
    def get_text(element):
        return element.text

    def wait_for_element_visible(self, locator):
        return self.webdriver_wait.until(EC.visibility_of_element_located(locator))

    def is_element_visible(self, locator):
        try:
            return self.driver.find_element(locator[0], locator[1])
        except Exception as err:
            return False

    def find_elements(self, locator):
        return self.driver.find_elements(locator[0], locator[1])

    @staticmethod
    def get_rect(element):
        return element.rect

    def right_or_left(self, element):
        pass

    def tap(self, x, y):
        touch_action = TouchAction(self.driver)
        touch_action.tap(x=x, y=y, count=1).release().perform()

    def double_tap_ele_to_get_details_message(self, x, y, try_count=5):
        message = None
        touch_action = TouchAction(self.driver)
        while try_count > 0:
            touch_action.tap(x=x, y=y, count=2).release().perform()
            ele = self.is_element_visible(AndroidMobilePageObject.details_message())
            if ele:
                print("Try to get details message")
                message = self.get_text(ele)
                print(message)
                self.click(ele)
                break
            try_count = try_count - 1

        if message:
            print("Success to get the details message")
        else:
            print("Failed to get the details message")

        return message


class AndroidMobilePageObject:

    def __init__(self):
        pass

    @staticmethod
    def search_btn_in_home_page():
        return (MobileBy.ID, "com.tencent.mm:id/f8y")

    @staticmethod
    def address_book_in_home_page():
        return (MobileBy.XPATH, "(//*[@resource-id='com.tencent.mm:id/cns'])[2]")

    @staticmethod
    def gongzong_number_item():
        return (MobileBy.XPATH, "(//*[@resource-id='com.tencent.mm:id/b3b'])[4]")

    @staticmethod
    def search_in_gongzong_page():
        return (MobileBy.ACCESSIBILITY_ID, "搜索")

    @staticmethod
    def search_input_in_gongzong_page():
        return (MobileBy.ID, "com.tencent.mm:id/bhn")

    @staticmethod
    def target_item():
        return (MobileBy.XPATH, "//android.widget.TextView[@text='大众汽车金融中国测试号']")

    @staticmethod
    def title_in_chat():
        return (MobileBy.ID, "com.tencent.mm:id/gas")

    @staticmethod
    def message_btn():
        return (MobileBy.ID, "com.tencent.mm:id/aly")

    @staticmethod
    def message_input():
        return (MobileBy.ID, "com.tencent.mm:id/al_")

    @staticmethod
    def message_send_btn():
        return (MobileBy.ID, "com.tencent.mm:id/anv")

    @staticmethod
    def latest_message():
        return (MobileBy.ID, "com.tencent.mm:id/ala")

    @staticmethod
    def details_message():
        return (MobileBy.ID, "com.tencent.mm:id/c9a")

    @staticmethod
    def contact_photo():
        return (MobileBy.ID, "com.tencent.mm:id/aku")


class AndroidProcess:

    def __init__(self, webdriver):
        self.driver = webdriver
        self.send_message_time = None
        self.get_reply_time = None
        self.mobile_function = MobileFunction(self.driver)

    def go_into_volkswagen_official_account(self):
        ele_address_book_btn = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.address_book_in_home_page()
        )
        self.mobile_function.click(ele_address_book_btn)

        ele_gongzong_number_item = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.gongzong_number_item()
        )
        self.mobile_function.click(ele_gongzong_number_item)

        ele_search_in_gongzong_page = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.search_in_gongzong_page()
        )
        self.mobile_function.click(ele_search_in_gongzong_page)

        ele_search_input_in_gongzong_page = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.search_input_in_gongzong_page()
        )
        self.mobile_function.send_text(ele_search_input_in_gongzong_page, "大众汽车金融中国测试号".decode("utf-8"))

        ele_target_item = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.target_item()
        )
        self.mobile_function.click(ele_target_item)

        ele_title_in_chat = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.title_in_chat())

    def send_message_then_calculating_time_taken_to_reply(self, value):

        ele_message = self.mobile_function.is_element_visible(AndroidMobilePageObject.message_btn())
        if ele_message:
            self.mobile_function.click(ele_message)

        ele_message_input = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.message_input())
        self.mobile_function.send_text(ele_message_input, value.decode("utf-8"))
        ele_message_send_btn = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.message_send_btn())
        self.mobile_function.click(ele_message_send_btn)
        time.sleep(0.1)
        self.send_message_time = time.time()

        retry_count = 10
        while retry_count > 0:
            contact_photos = self.mobile_function.find_elements(AndroidMobilePageObject.contact_photo())
            if len(contact_photos) > 0 and self.mobile_function.get_rect(contact_photos[-1])["x"] < 500:
                self.get_reply_time = time.time()
                break
        if self.get_reply_time:
            print("Cost time is: " + str(self.get_reply_time - self.send_message_time))
            self.get_reply_time = None
        else:
            print("Failed to get the cost time")


class CaseDataModel:

    def __init__(self, case_no, send_message, reply, link_template_screenshot_folder, link_template_screenshot,
                 reply_from_script, link_from_script, screenshot_from_script, link_screenshot_from_script):
        self.case_no = case_no
        self.send_message = send_message
        self.reply = reply
        self.link_template_screenshot_folder = link_template_screenshot_folder
        self.link_template_screenshot = link_template_screenshot
        self.reply_from_script = reply_from_script
        self.link_from_script = link_from_script
        self.screenshot_from_script = screenshot_from_script
        self.link_screenshot_from_script = link_screenshot_from_script


if __name__ == '__main__':

    desired_caps_android_wechart = {
        "platformName": "Android",
        "platformVersion": "9",
        "automationName": "Appium",
        "appActivity": "com.tencent.mm.ui.LauncherUI",
        "appPackage": "com.tencent.mm",
        "deviceName": "AKC7N18907000186",
        "newCommandTimeout": 7200,
        "noReset": True,
        'chromeOptions': {'androidProcess': 'com.tencent.mm:tools'}
    }

    # driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps_android_wechart)

    #android_process = AndroidProcess(driver)
    #android_process.send_message_then_calculating_time_taken_to_reply("你好")
    #mobile_function = MobileFunction(driver)

    current_screenshot = PATH(os.path.join("screenshot", "case1.png"))
    #driver.save_screenshot(current_screenshot)

    location = Utils.match_image(current_screenshot, PATH(os.path.join("template", "huaweip20pro", "case1_link1.png")))

    #android_process = AndroidProcess(driver)
    #android_process.go_into_volkswagen_official_account()
    test_data_list = Utils.load_data_from_excel(PATH("test_case_example.xlsx"))
    print("Finished")

