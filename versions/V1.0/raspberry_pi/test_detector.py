import cv2
import numpy as np
import time

from camera import init_camera, read_frame, release_camera
from detector import detect_target
from controller import compute_command
from serial_sender import open_serial, send_command, read_reply, close_serial


def main():
    picam2 = None
    ser = None

    # ========== 串口开关 ==========
    SERIAL_ENABLE = True

    # 串口配置
    SERIAL_PORT = "/dev/ttyUSB0"
    SERIAL_BAUDRATE = 115200
    SERIAL_TIMEOUT = 1.0

    # ========== 发送节流 ==========
    SEND_INTERVAL = 0.03
    last_send_time = 0

    # ========== 丢失目标逻辑 ==========
    LOST_THRESHOLD = 10
    lost_count = 0
    tracker_state = "TRACKING"
    home_sent = False

    # ========== 自动触发 OUT ==========
    OUT_HOLD_TIME = 2.0       # 稳定保持 2 秒后触发 OUT
    DONE_DISPLAY_TIME = 1.0   # 触发 OUT 后显示完成状态 1 秒
    out_sent = False
    done_start_time = None

    # ========== 颜色阈值 ==========
    color_lower = np.array([0, 120, 70])
    color_upper = np.array([10, 255, 255])

    # ========== 控制参数 ==========
    config = {
        "DEADZONE_X": 15,
        "DEADZONE_Y": 15,

        "THRESHOLD_X_SMALL": 40,
        "THRESHOLD_X_MEDIUM": 100,
        "THRESHOLD_Y_SMALL": 40,
        "THRESHOLD_Y_MEDIUM": 100,

        "STEP_SMALL": 6,
        "STEP_MEDIUM": 15,
        "STEP_LARGE": 30
    }

    # ========== 防抖参数 ==========
    SMOOTH_ALPHA = 0.25

    STABLE_ENTER_X = 10
    STABLE_ENTER_Y = 10

    STABLE_EXIT_X = 20
    STABLE_EXIT_Y = 20

    is_stable = False
    stable_start_time = None

    smooth_tx = None
    smooth_ty = None

    try:
        picam2 = init_camera(640, 480)

        if SERIAL_ENABLE:
            ser = open_serial(SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT)

        while True:
            ret, frame = read_frame(picam2)
            if not ret:
                print("读取图像失败")
                continue

            current_command = "+0,+0"
            stable_elapsed = 0.0

            result = detect_target(frame, color_lower, color_upper, min_area=300)

            # ========== 如果目标已经完成，先保持显示一小段时间 ==========
            if tracker_state == "TARGET_DONE":
                elapsed_done = 0.0
                if done_start_time is not None:
                    elapsed_done = time.time() - done_start_time

                cv2.putText(
                    frame, "STATE=TARGET_DONE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                )
                cv2.putText(
                    frame, f"done_hold={elapsed_done:.2f}s", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
                )

                print(f"[TARGET_DONE] done_hold={elapsed_done:.2f}s")

                if elapsed_done >= DONE_DISPLAY_TIME:
                    tracker_state = "TRACKING"
                    out_sent = False
                    done_start_time = None
                    is_stable = False
                    stable_start_time = None

                cv2.imshow("Target Detection", frame)
                cv2.imshow("Mask", result["mask"])

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                continue

            # ========== 找到目标 ==========
            if result["found"]:
                tracker_state = "TRACKING"
                lost_count = 0
                home_sent = False

                x, y, w, h = result["bbox"]
                tx, ty = result["target_center"]

                # ---------- 目标中心平滑 ----------
                if smooth_tx is None or smooth_ty is None:
                    smooth_tx = float(tx)
                    smooth_ty = float(ty)
                else:
                    smooth_tx = SMOOTH_ALPHA * tx + (1 - SMOOTH_ALPHA) * smooth_tx
                    smooth_ty = SMOOTH_ALPHA * ty + (1 - SMOOTH_ALPHA) * smooth_ty

                smoothed_center = (int(smooth_tx), int(smooth_ty))

                control_result = compute_command(frame, smoothed_center, config)
                current_command = control_result["command"]

                dx = control_result["dx"]
                dy = control_result["dy"]

                # ---------- 稳定区迟滞判断 ----------
                if not is_stable:
                    if abs(dx) <= STABLE_ENTER_X and abs(dy) <= STABLE_ENTER_Y:
                        is_stable = True
                        stable_start_time = time.time()
                else:
                    if abs(dx) > STABLE_EXIT_X or abs(dy) > STABLE_EXIT_Y:
                        is_stable = False
                        stable_start_time = None
                        out_sent = False

                if is_stable and stable_start_time is not None:
                    stable_elapsed = time.time() - stable_start_time
                else:
                    stable_elapsed = 0.0

                # ---------- 自动触发 OUT ----------
                if is_stable and stable_elapsed >= OUT_HOLD_TIME and not out_sent:
                    if SERIAL_ENABLE:
                        send_command(ser, "OUT")
                        reply1, reply2 = read_reply(ser)

                        if reply1:
                            print("收到:", reply1)
                        if reply2:
                            print("收到:", reply2)

                    out_sent = True
                    tracker_state = "TARGET_DONE"
                    done_start_time = time.time()

                # ---------- 画图 ----------
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (tx, ty), 5, (0, 0, 255), -1)
                cv2.circle(frame, smoothed_center, 5, (255, 0, 255), -1)

                cx, cy = control_result["frame_center"]
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.line(frame, (cx, cy), smoothed_center, (255, 255, 255), 1)

                stable_text = "YES" if is_stable else "NO"

                info_text_1 = f"STATE={tracker_state}"
                info_text_2 = f"dx={dx} dy={dy}"
                info_text_3 = f"cmd={current_command}"
                info_text_4 = f"stable={stable_text} hold={stable_elapsed:.2f}s"

                cv2.putText(
                    frame, info_text_1, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )
                cv2.putText(
                    frame, info_text_2, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2
                )
                cv2.putText(
                    frame, info_text_3, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
                )
                cv2.putText(
                    frame, info_text_4, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2
                )

                print(
                    f"[{tracker_state}] "
                    f"raw=({tx},{ty}) smooth=({smoothed_center[0]},{smoothed_center[1]}) "
                    f"dx={dx} dy={dy} cmd={current_command} "
                    f"stable={stable_text} hold={stable_elapsed:.2f}s out_sent={out_sent}"
                )

                # ---------- 串口发送跟踪命令 ----------
                if SERIAL_ENABLE:
                    current_time = time.time()
                    interval_ok = (current_time - last_send_time) >= SEND_INTERVAL

                    # 稳定区里不再微调；触发 OUT 后也不再微调
                    if interval_ok and current_command != "+0,+0" and not is_stable and not out_sent:
                        send_command(ser, current_command)
                        reply1, reply2 = read_reply(ser)

                        if reply1:
                            print("收到:", reply1)
                        if reply2:
                            print("收到:", reply2)

                        last_send_time = current_time

            # ========== 未找到目标 ==========
            else:
                lost_count += 1

                smooth_tx = None
                smooth_ty = None

                is_stable = False
                stable_start_time = None
                out_sent = False

                if lost_count < LOST_THRESHOLD:
                    tracker_state = "LOST_WAIT"
                else:
                    tracker_state = "LOST_HOME"

                info_text_1 = f"STATE={tracker_state}"
                info_text_2 = f"lost_count={lost_count}"
                info_text_3 = f"cmd={current_command}"

                cv2.putText(
                    frame, info_text_1, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                )
                cv2.putText(
                    frame, info_text_2, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2
                )
                cv2.putText(
                    frame, info_text_3, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2
                )

                print(f"[{tracker_state}] 未检测到目标, lost_count={lost_count}")

                if SERIAL_ENABLE and tracker_state == "LOST_HOME" and not home_sent:
                    send_command(ser, "HOME")
                    reply1, reply2 = read_reply(ser)

                    if reply1:
                        print("收到:", reply1)
                    if reply2:
                        print("收到:", reply2)

                    home_sent = True

            cv2.imshow("Target Detection", frame)
            cv2.imshow("Mask", result["mask"])

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        release_camera(picam2)
        close_serial(ser)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
