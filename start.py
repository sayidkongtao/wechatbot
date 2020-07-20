# encoding: utf-8
import numpy as np
import cv2 as cv
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

touch_action = TouchAction(driver)


def double_tap_ele(try_count=5, x=780, y=2040):
    get_details = False
    mobile_function = MobileFunction()

    while try_count > 0:
        touch_action.tap(x=x, y=y, count=2).release().perform()
        ele = mobile_function.is_element_visible(AndroidMobilePageObject.details_message())
        if ele:
            print("Get details messge")
            print(mobile_function.get_text(ele))
            break
        try_count = try_count - 1


class MobileFunction:

    webdriver_wait = WebDriverWait(driver, 30)

    def __init__(self):
        pass

    def click(self, element):
        element.click()

    def send_text(self, element, value):
        element.send_keys(value)

    def get_text(self, element):
        return element.text

    def wait_for_element_visible(self, locator):
        return self.webdriver_wait.until(EC.visibility_of_element_located(locator))

    def is_element_visible(self, locator):
        try:
            return driver.find_element(locator[0], locator[1])
        except Exception as err:
            return False

    @staticmethod
    def get_rect(self, element):
        return element.rect

    def right_or_left(self, element):
        pass


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

double_tap_ele()

print(11)

#https://www.cnblogs.com/BlueSkyyj/p/8651365.html