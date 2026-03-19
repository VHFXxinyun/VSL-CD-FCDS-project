import serial
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 115200

SERIAL_TIMEOUT = 1
INIT_DELAY = 2

SPECIAL_COMMANDS = {'HOME', 'OUT'}


def open_serial():
    """打开串口"""
    ser = serial.Serial(PORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
    time.sleep(INIT_DELAY)
    print(f"串口已打开: {PORT}")
    return ser


def send_command(ser, cmd: str):
    """发送一条串口命令"""
    message = cmd + '\n'
    ser.write(message.encode('utf-8'))
    print("已发送:", cmd)


def read_reply(ser):
    """读取 ESP32 的两行回复"""
    reply1 = ser.readline().decode('utf-8', errors='ignore').strip()
    reply2 = ser.readline().decode('utf-8', errors='ignore').strip()

    if reply1:
        print("收到:", reply1)
    if reply2:
        print("收到:", reply2)


def is_valid_increment_command(cmd: str) -> bool:
    """
    检查是否为合法格式:
    +15,-24
    0,+10
    -8,0
    """
    parts = cmd.split(',')

    if len(parts) != 2:
        return False

    pan_str = parts[0].strip()
    tilt_str = parts[1].strip()

    if len(pan_str) == 0 or len(tilt_str) == 0:
        return False

    try:
        int(pan_str)
        int(tilt_str)
    except ValueError:
        return False

    return True


def main():
    ser = None
    try:
        ser = open_serial()

        while True:
            cmd = input("输入命令(+15,-24 / HOME / OUT)(输入 q 退出): ").strip()

            if not cmd:
                continue

            cmd_upper = cmd.upper()

            if cmd_upper == 'Q':
                print("退出程序")
                break

            # 特殊命令
            if cmd_upper in SPECIAL_COMMANDS:
                send_command(ser, cmd_upper)
                read_reply(ser)
                continue

            # 增量命令
            if is_valid_increment_command(cmd):
                send_command(ser, cmd)
                read_reply(ser)
            else:
                print("无效命令格式。")
                print("正确示例: +15,-24")
                print("或输入: HOME / OUT / q")

    except Exception as e:
        print("出错:", e)

    finally:
        if ser and ser.is_open:
            ser.close()
            print("串口已关闭")


if __name__ == '__main__':
    main()
