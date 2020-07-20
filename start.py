# encoding: utf-8
import numpy as np
import cv2
from appium import webdriver
import time
import os
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction


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

    @staticmethod
    def is_element_visible(self, locator):
        try:
            return self.driver.find_element(locator[0], locator[1])
        except Exception as err:
            return False

    @staticmethod
    def get_rect(element):
        return element.rect

    def right_or_left(self, element):
        pass

    @staticmethod
    def tap(x, y):
        touch_action = TouchAction(driver)
        touch_action.tap(x=x, y=y, count=1).release().perform()

    def double_tap_ele_to_get_details_message(self, x, y, try_count=5):
        message = None
        touch_action = TouchAction(driver)
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
        return (MobileBy.XPATH, "//*[@text='大众汽车金融中国测试号']")

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


if __name__ == '__main__':

    desired_caps_android_wechart = {
        "platformName": "Android",
        "platformVersion": "9",
        "automationName": "Appium",
        "appActivity": "com.tencent.mm.ui.LauncherUI",
        "appPackage": "com.tencent.mm",
        "deviceName": "AKC7N18907000186",
        "newCommandTimeout": 7200,
        "noReset": True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps_android_wechart)

    mobile_function = MobileFunction(driver)

    current_screenshot = PATH(os.path.join("template", "current.png"))
    driver.save_screenshot(current_screenshot)

    location = Utils.match_image(current_screenshot, PATH(os.path.join("template", "huawei_p20", "image_1.png")))
    print("11")
