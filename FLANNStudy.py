# coding=utf-8
import numpy as np
import cv2
import os
from matplotlib import pyplot as plt

# https://blog.csdn.net/zhuisui_woxin/article/details/84400439
PATH = lambda path: os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        path
    )
)

query_image = cv2.imread(PATH(r"template\huaweip20pro\case1_link1.png"), 0)
# 读取要匹配的灰度照片
training_image = cv2.imread(PATH(r"screenshot\case1.png"), 0)
# 创建sift检测器
sift = cv2.xfeatures2d.SIFT_create()
kp1, des1 = sift.detectAndCompute(query_image, None)
kp2, des2 = sift.detectAndCompute(training_image, None)
# 设置Flannde参数
FLANN_INDEX_KDTREE = 0
indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
searchParams = dict(checks=50)
flann = cv2.FlannBasedMatcher(indexParams, searchParams)
matches = flann.knnMatch(des1, des2, k=2)

# 设置好初始匹配值
matchesMask = [[0, 0] for i in range(len(matches))]
for i, (m, n) in enumerate(matches):
    if m.distance < 0.5 * n.distance:  # 舍弃小于0.5的匹配结果
        matchesMask[i] = [1, 0]
drawParams = dict(matchColor=(0, 0, 255), singlePointColor=(255, 0, 0), matchesMask=matchesMask,
                  flags=0)  # 给特征点和匹配的线定义颜色
resultimage = cv2.drawMatchesKnn(query_image, kp1, training_image, kp2, matches, None, **drawParams)  # 画出匹配的结果
plt.imshow(resultimage, ), plt.show()
