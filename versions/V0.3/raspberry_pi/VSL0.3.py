import serial
import time

PORT = '/dev/ttyUSB0'       #初始化串口信息
BAUDRATE = 115200

SERIAL_TIMEOUT = 1
INIT_DELAY = 2

VALID_COMMANDS = {'RIGHT', 'LEFT', 'UP', 'DOWN', 'HOME', 'OUT'}


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


def main():
    ser = None
    try:
        ser = open_serial()

        while True:
            cmd = input("输入命令(RIGHT LEFT UP DOWN HOME OUT)(输入 q 退出): ").strip()

            if not cmd:
                continue

            cmd_upper = cmd.upper()

            if cmd_upper == 'Q':
                print("退出程序")
                break

            if cmd_upper not in VALID_COMMANDS:
                print("无效命令，请输入 RIGHT / LEFT / UP / DOWN / HOME / OUT / q")
                continue

            send_command(ser, cmd_upper)
            read_reply(ser)

    except Exception as e:
        print("出错:", e)

    finally:
        if ser and ser.is_open:
            ser.close()
            print("串口已关闭")


if __name__ == '__main__':
    main()
