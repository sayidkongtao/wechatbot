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

query_image = cv2.imread(PATH(r"template\huaweip20pro\case1_link6.png"), 0)
# 读取要匹配的灰度照片
training_image = cv2.imread(PATH(r"screenshot\case1.png"), 0)


# 基于FLANN的匹配器(FLANN based Matcher)描述特征点
def fun1():
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


def fun2():
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
        cv2.polylines(training_image, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        print 3
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
    #     matchesMask = None
    # draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matchesMask, flags=2)
    # result = cv2.drawMatches(query_image, kp1, training_image, kp2, good, None, **draw_params)
    # plt.imshow(result, 'gray')
    # plt.show()


if __name__ == '__main__':
    fun2()