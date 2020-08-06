# coding=utf-8

import cv2
import numpy as np
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
import re
from urllib import unquote
PATH = lambda path: os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        path
    )
)
# a = """
# 👉 <a href="https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc48ed8d2ff9e52fd&redirect_uri=https%3a%2f%2fwechat.volkswagen-finance-china.com.cn%2fCCG%2fHome?utm_source=chatbot%26utm_medium=cpc%26utm_content=textlink%26utm_campaign=contract%26utm_term=还款计划_合同信息&response_type=code&scope=snsapi_base&state=1#wechat_redirect">- 查询合同信息与还款计划表</a>
#
# 👉 <a href="https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc48ed8d2ff9e52fd&redirect_uri=https%3a%2f%2fwechat.volkswagen-finance-china.com.cn%2fCCG%2fOverduePayment%2fIndex?utm_source=chatbot%26utm_medium=cpc%26utm_content=textlink%26utm_campaign=overdue%26utm_term=还款进度_逾期合同还款&response_type=code&scope=snsapi_base&state=1#wechat_redirect">- 逾期合同还款</a>
#
# 👉 <a href="https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc48ed8d2ff9e52fd&redirect_uri=https%3a%2f%2fwechat.volkswagen-finance-china.com.cn%2fCCG%2fPayTrial?utm_source=chatbot%26utm_medium=cpc%26utm_content=textlink%26utm_campaign=prepayment%26utm_term=还款进度_提前还款查询&response_type=code&scope=snsapi_base&state=1#wechat_redirect">- 提前还款报价</a>
# """
#
# pattern = re.compile(r'<a.*?href="(.*?)".*?>(.*?)</a>')
#
# find_content_list = re.findall(pattern, a)
#
# for find_content in find_content_list:
#     print(find_content[0], find_content[1])
#
# print(a)
#
# b = a.replace(find_content_list[0][0], "").replace(find_content_list[1][0], "").replace(find_content_list[2][0], "").replace('<a href="">', "").replace("</a>", "")


def match_image_by_match_template_func(source_path, template_path, mobile_window_rect=None,
                                       method=cv2.TM_CCOEFF_NORMED):
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
        x = final_location[-1]["x"] + final_location[-1]["width"] / 3
        y = final_location[-1]["y"] + final_location[-1]["height"] / 3

        if mobile_window_rect:
            mobile_window_width = mobile_window_rect["width"]
            mobile_window_height = mobile_window_rect["height"]
            h, w = source.shape
            x = x * mobile_window_width / w
            y = y * mobile_window_height / h

        return {"x": x, "y": y}
    else:
        return None

# C:\Users\Administrator\PycharmProjects\wechatbot\template\huaweip20pro\copy_item\copy_item.png
# match_image_by_match_template_func(PATH(r"../screenshot/case1.png"), PATH(r"../template/huaweip20pro/case1_link1.png"))
match_image_by_match_template_func(PATH(r"../backup/copy3.png"), PATH(r"../template/huaweip20pro/copy_item/copy_item.png"))
