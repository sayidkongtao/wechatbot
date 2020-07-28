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
import logging

reload(sys)
sys.setdefaultencoding('utf8')

PATH = lambda path: os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        path
    )
)

logging.basicConfig(filename=PATH(os.path.join("log", "example.log")),
                    level=logging.INFO,
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def get_tap_coordinate(source_path, template_path):
        # todo: need to update function
        Utils.match_image_by_flann_func(source_path, template_path)

    @staticmethod
    def match_image_by_match_template_func(source_path, template_path, method=cv2.TM_CCOEFF_NORMED):
        """

        :param source_path:
        :param template_path:
        :param method:
        :return:
        """
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

        if len(final_location) > 0:
            return {"x": final_location[0]["x"] + final_location[0]["width"] / 2,
                    "y": final_location[0]["y"] + final_location[0]["height"] / 2}
        else:
            return None

    @staticmethod
    def match_image_by_flann_func(source_path, template_path):
        """
        :param source_path:
        :param template_path:
        :return:
        """
        query_image = cv2.imread(PATH(template_path), 0)
        # 读取要匹配的灰度照片
        training_image = cv2.imread(PATH(source_path), 0)

        MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量为10
        # Initiate SIFT detector创建sift检测器
        sift = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(query_image, None)
        kp2, des2 = sift.detectAndCompute(training_image, None)
        # 创建设置FLANN匹配
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        # 舍弃小于0.7的匹配
        for m, n in matches:
            if m.distance > 0.7 * n.distance:
                good.append(m)

        if len(good) > MIN_MATCH_COUNT:
            # 获取关键点的坐标
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            # 计算变换矩阵和MASK
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            # matchesMask = mask.ravel().tolist()
            h, w = query_image.shape
            # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)
            loc = (np.int32(dst[0][0]), np.int32(dst[2][0]))
            return {"x": (np.int32(dst[2][0])[0] + np.int32(dst[0][0])[0]) / 2, "y": (np.int32(dst[2][0])[1] +
                                                                                      np.int32(dst[0][0])[1]) / 2}
        else:
            print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
            return None

    @staticmethod
    def load_data_from_excel(file_name):
        """

        :param file_name:
        :return:
        """
        wb = load_workbook(file_name)
        work_sheet = wb[wb.sheetnames[0]]
        test_data = []
        flag_count = 0
        for row in work_sheet.values:
            if flag_count == 0:
                test_data.append(CaseDataModel(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                               row[9]))
                flag_count = flag_count + 1
            else:
                test_data.append(CaseDataModel(row[0], row[1], row[2], row[3], row[4], None, None, None, None, None))
        wb.close()
        return test_data

    @staticmethod
    def write_data_into_excel(file_name, data_list, start_row=2):
        """

        :param file_name:
        :param data_list:
        :param start_row:
        :return:
        """
        wb = load_workbook(file_name)
        work_sheet = wb[wb.sheetnames[0]]
        for data in data_list:
            work_sheet["F" + str(start_row)] = data.reply_from_script
            work_sheet["G" + str(start_row)] = data.link_from_script
            work_sheet["H" + str(start_row)] = data.screenshot_from_script
            work_sheet["I" + str(start_row)] = data.link_screenshot_from_script
            work_sheet["J" + str(start_row)] = data.reply_cost_time_from_script
            start_row = start_row + 1
        wb.save(file_name)


class MobileFunction:

    def __init__(self, driver):
        """

        :param driver:
        """
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

    def double_tap_ele_to_get_details_message(self, x, y, try_count=20):
        message = None
        touch_action = TouchAction(self.driver)
        print("The details_message coordinate is {} {}".format(x,y))
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
            time.sleep(1)

        if message:
            print("Success to get the details message")
        else:
            print("Failed to get the details message")

        return message

    def save_screenshot_as_png(self, file_name):
        self.driver.save_screenshot(filename=file_name)


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

    @staticmethod
    def back_btn():
        return (MobileBy.ID, "com.tencent.mm:id/dn")


class AndroidProcess:

    def __init__(self, webdriver):
        self.driver = webdriver
        self.send_message_time = None
        self.get_reply_time = None
        self.mobile_function = MobileFunction(self.driver)

    def go_into_volkswagen_official_account(self, count_name):
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
        # "大众汽车金融中国测试号"
        self.mobile_function.send_text(ele_search_input_in_gongzong_page, count_name.decode("utf-8"))

        ele_target_item = self.mobile_function.wait_for_element_visible(
            AndroidMobilePageObject.target_item()
        )
        self.mobile_function.click(ele_target_item)

        ele_title_in_chat = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.title_in_chat())

    def send_message_then_calculating_time_taken_to_reply(self, value):
        value = value.decode("utf-8")
        print("Send the message: " + value)
        self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.title_in_chat())
        time.sleep(1)
        ele_message = self.mobile_function.is_element_visible(AndroidMobilePageObject.message_btn())
        if ele_message:
            self.mobile_function.click(ele_message)

        ele_message_input = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.message_input())
        self.mobile_function.send_text(ele_message_input, value)
        ele_message_send_btn = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.message_send_btn())
        self.mobile_function.click(ele_message_send_btn)
        time.sleep(0.1)
        self.send_message_time = time.time()

        while time.time() - self.send_message_time < 30:
            contact_photos = self.mobile_function.find_elements(AndroidMobilePageObject.contact_photo())
            if len(contact_photos) > 0 and self.mobile_function.get_rect(contact_photos[-1])["x"] < 500:
                self.get_reply_time = time.time()
                break
        if self.get_reply_time:
            cost_time = str(self.get_reply_time - self.send_message_time)
            print("Cost time is: " + cost_time)
            self.get_reply_time = None
            return cost_time
        else:
            print("Failed to get the cost time after 30s")
            return None

    def deal_with_test_data(self, data):
        """

        :param data:
        :return:
        """
        print("Start to deal with case: " + data.case_no)

        # 发送的信息并获取回复时间
        result_reply = self.send_message_then_calculating_time_taken_to_reply(data.send_message)
        if result_reply:
            # J 给reply_cost_time_from_script赋值
            data.reply_cost_time_from_script = result_reply
        else:
            data.reply_cost_time = "Failed to get the cost time after 30s"

        # 不管获取消息成功与否，都进行截图
        current_screenshot = PATH(os.path.join("screenshot", "case" + str(data.case_no) + ".png"))
        self.mobile_function.save_screenshot_as_png(current_screenshot)
        # H 给screenshot_from_script赋值
        data.screenshot_from_script = os.path.join("screenshot", "case" + str(data.case_no) + ".png")

        # 获取回复的信息
        if result_reply:
            latest_message = self.mobile_function.find_elements(AndroidMobilePageObject.latest_message())
            rect = self.mobile_function.get_rect(latest_message[-1])
            x = rect["x"] + rect["width"] - 20
            y = rect["y"] + rect["height"] - 20
            message = self.mobile_function.double_tap_ele_to_get_details_message(x=x, y=y, try_count=20)
            # F 给reply_from_script赋值
            data.reply_from_script = message
            # 退回到聊天窗口
            self.mobile_function.tap(x, y)

            # 处理回复消息中的link
            link_template_screenshot_list = data.link_template_screenshot.split("\n")
            link_screenshot_flag = 1
            link_screenshot_list = []
            for link_template_screenshot in link_template_screenshot_list:
                # 获取 link样例图片在原图中的坐标
                loc = Utils.match_image_by_flann_func(current_screenshot,
                                                      PATH(os.path.join("template", "common", link_template_screenshot)))

                current_link_screenshot = os.path.join("screenshot", "case{}_link{}.png".format(data.case_no,
                                                                                                link_screenshot_flag))
                # 点击匹配到的link
                if loc:
                    try:
                        self.mobile_function.tap(loc["x"], loc["y"])
                        # 等待页面加载
                        time.sleep(5)
                        self.mobile_function.save_screenshot_as_png(PATH(current_link_screenshot))

                        # 从link页面返回到消息界面
                        back_btn = self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.back_btn())
                        self.mobile_function.click(back_btn)
                        self.mobile_function.wait_for_element_visible(AndroidMobilePageObject.title_in_chat())
                    except Exception as e:
                        print(e)
                        back_btn = self.mobile_function.is_element_visible(AndroidMobilePageObject.back_btn())
                        if back_btn:
                            self.mobile_function.click(back_btn)

                        print("No link template matched for: " + current_link_screenshot)
                        current_link_screenshot = "No link template matched for: " + current_link_screenshot
                else:
                    print("No link template matched for: " + current_link_screenshot)
                    current_link_screenshot = "No link template matched for: " + current_link_screenshot

                link_screenshot_flag = link_screenshot_flag + 1
                link_screenshot_list.append(current_link_screenshot)

            if len(link_screenshot_list) > 0:
                # I 给link_screenshot_from_script赋值
                data.link_screenshot_from_script = "\n".join(link_screenshot_list)

    def _init_test_data(self, data):
        pass


class CaseDataModel:

    def __init__(self, case_no, send_message, reply, link_template_screenshot_folder, link_template_screenshot,
                 reply_from_script, link_from_script, screenshot_from_script, link_screenshot_from_script,
                 reply_cost_time_from_script):
        self.case_no = str(case_no)
        self.send_message = send_message
        self.reply = reply
        self.link_template_screenshot_folder = link_template_screenshot_folder
        self.link_template_screenshot = link_template_screenshot
        self.reply_from_script = reply_from_script
        self.link_from_script = link_from_script
        self.screenshot_from_script = screenshot_from_script
        self.link_screenshot_from_script = link_screenshot_from_script
        self.reply_cost_time_from_script = reply_cost_time_from_script


def clean_data():
    del_list = os.listdir(PATH("screenshot"))
    for f in del_list:
        file_path = os.path.join(PATH("screenshot"), f)
        os.remove(file_path)


def android_steps():
    desired_caps_android_wechat = {
        "platformName": "Android",
        "platformVersion": "10",
        "automationName": "Appium",
        "appActivity": "com.tencent.mm.ui.LauncherUI",
        "appPackage": "com.tencent.mm",
        "deviceName": "AKC7N18907000186",
        "newCommandTimeout": 7200,
        "noReset": True,
        'chromeOptions': {'androidProcess': 'com.tencent.mm:tools'}
    }

    # 1. 从excel读取数据
    test_data_list = Utils.load_data_from_excel(PATH("test_case_example.xlsx"))
    test_data_list_copy = test_data_list[1:]
    print("Total cases: " + str(len(test_data_list_copy)))

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps_android_wechat)
    android_process = AndroidProcess(driver)

    # 2. 进入公众号
    android_process.go_into_volkswagen_official_account("大众汽车金融中国测试号")

    # 3. 处理消息
    for test_data in test_data_list_copy:
        try:
            android_process.deal_with_test_data(test_data)
        except Exception as e:
            print(e)
            # 需要判断是否回到主界面

    #数据写进excel
    Utils.write_data_into_excel(PATH("test_case_example.xlsx"), test_data_list_copy)
    print("write_data_into_excel")


if __name__ == '__main__':
    clean_data()
    android_steps()
    print("Finished: ")
