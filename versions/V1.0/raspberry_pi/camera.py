from picamera2 import Picamera2
import time
import cv2


def init_camera(width: int = 640, height: int = 480):
    """
    初始化 CSI 摄像头
    返回 Picamera2 对象
    """
    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={"size": (width, height), "format": "RGB888"}
    )

    picam2.configure(config)
    picam2.start()

    # 给摄像头一点稳定时间
    time.sleep(1)

    return picam2


def read_frame(picam2):
    """
    读取一帧图像
    返回:
        ret   -> 是否成功
        frame -> 图像帧
    """
    try:
        frame = picam2.capture_array()

        # 这里先不要做 RGB -> BGR 转换
        # 因为你当前实测发现转换后红色会变蓝色
        # 说明这一步在你当前环境下可能是多余的
        return True, frame

    except Exception:
        return False, None


def release_camera(picam2):
    """
    释放摄像头资源
    """
    if picam2 is not None:
        picam2.stop()


def test_camera():
    """
    独立测试函数
    按 q 退出
    """
    picam2 = None

    try:
        picam2 = init_camera(640, 480)

        while True:
            ret, frame = read_frame(picam2)

            if not ret:
                print("读取图像失败")
                continue

            cv2.imshow("CSI Camera Preview", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        release_camera(picam2)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    test_camera()
