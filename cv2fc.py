import cv2
import numpy as np


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
