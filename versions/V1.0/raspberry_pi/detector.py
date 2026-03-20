import cv2
import numpy as np


def find_largest_contour(mask):
    """
    在二值掩膜图中寻找最大轮廓
    返回:
        largest_contour -> 最大轮廓对象，若没有则为 None
        max_area        -> 最大轮廓面积
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, 0

    largest_contour = max(contours, key=cv2.contourArea)
    max_area = cv2.contourArea(largest_contour)

    return largest_contour, max_area


def get_contour_center(contour):
    """
    根据轮廓计算中心点
    返回:
        (cx, cy) 或 None
    """
    if contour is None:
        return None

    M = cv2.moments(contour)

    # 防止除零
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    return (cx, cy)


def detect_target(frame, color_lower, color_upper, min_area=300):
    """
    检测目标色块

    输入:
        frame        -> 当前图像帧
        color_lower  -> HSV 下阈值，例如 np.array([0, 120, 70])
        color_upper  -> HSV 上阈值，例如 np.array([10, 255, 255])
        min_area     -> 最小有效面积，过滤小噪声

    输出:
        {
            "found": bool,
            "target_center": (tx, ty) or None,
            "bbox": (x, y, w, h) or None,
            "mask": mask,
            "area": area
        }
    """
    # 1. BGR -> HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 2. 颜色阈值分割，得到二值图
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # 3. 形态学操作，减少噪声
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # 4. 寻找最大轮廓
    contour, area = find_largest_contour(mask)

    # 5. 面积太小，认为没找到有效目标
    if contour is None or area < min_area:
        return {
            "found": False,
            "target_center": None,
            "bbox": None,
            "mask": mask,
            "area": area
        }

    # 6. 获取边框
    x, y, w, h = cv2.boundingRect(contour)

    # 7. 获取中心点
    center = get_contour_center(contour)

    return {
        "found": True,
        "target_center": center,
        "bbox": (x, y, w, h),
        "mask": mask,
        "area": area
    }
