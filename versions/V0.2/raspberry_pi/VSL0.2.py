from gpiozero import DigitalOutputDevice
import time

# =========================
# Raspberry Pi GPIO Sender
# Stable version
# =========================

# BCM pin mapping
SEND_PIN_1 = 17
SEND_PIN_2 = 18
SEND_PIN_3 = 27
SEND_PIN_4 = 22
SEND_PIN_5 = 4   # laser

PULSE_DURATION = 0.1
VALID_COMMANDS = {"0", "1", "2", "3", "4", "5", "6", "q", "quit", "exit"}


class GPIOSender:
    def __init__(self):
        self.output_pin_1 = DigitalOutputDevice(SEND_PIN_1, active_high=True, initial_value=False)
        self.output_pin_2 = DigitalOutputDevice(SEND_PIN_2, active_high=True, initial_value=False)
        self.output_pin_3 = DigitalOutputDevice(SEND_PIN_3, active_high=True, initial_value=False)
        self.output_pin_4 = DigitalOutputDevice(SEND_PIN_4, active_high=True, initial_value=False)
        self.output_pin_5 = DigitalOutputDevice(SEND_PIN_5, active_high=True, initial_value=False)

        self.all_pins = [
            self.output_pin_1,
            self.output_pin_2,
            self.output_pin_3,
            self.output_pin_4,
            self.output_pin_5,
        ]

        print("树莓派发送器就绪。输入 0~6 控制，输入 q 退出。")

    def safe_all_off(self):
        """Safely turn off all pins."""
        for pin in self.all_pins:
            try:
                pin.off()
            except Exception:
                pass

    def pulse(self, *pins, duration=PULSE_DURATION):
        """Turn on one or more pins for a short duration, then turn them off."""
        # 先清空，避免前一次动作残留状态影响当前动作
        self.safe_all_off()

        try:
            for pin in pins:
                pin.on()
            time.sleep(duration)
        finally:
            for pin in pins:
                try:
                    pin.off()
                except Exception:
                    pass

    def laser_on(self):
        self.output_pin_5.on()
        print("发送激光")

    def laser_off(self):
        self.output_pin_5.off()
        print("关闭激光")

    def reset_position(self):
        print("复位")
        self.pulse(self.output_pin_1, self.output_pin_2, self.output_pin_3, self.output_pin_4)

    def send_signal(self, command: int):
        if command == 1:
            print("向右")
            self.pulse(self.output_pin_1, self.output_pin_2)

        elif command == 2:
            print("向左")
            self.pulse(self.output_pin_3, self.output_pin_4)

        elif command == 3:
            print("向下")
            self.pulse(self.output_pin_1, self.output_pin_4)

        elif command == 4:
            print("向上")
            self.pulse(self.output_pin_2, self.output_pin_3)

        elif command == 5:
            self.laser_on()

        elif command == 6:
            self.laser_off()

        elif command == 0:
            self.reset_position()

        else:
            print("无效输入，请输入 0、1、2、3、4、5、6 或 q。")

    def close(self):
        """Safely release all GPIO resources."""
        self.safe_all_off()
        for pin in self.all_pins:
            try:
                pin.close()
            except Exception:
                pass
        print("GPIO已清理。")


def parse_command(user_input: str):
    """Parse and validate user input."""
    s = user_input.strip().lower()

    if s not in VALID_COMMANDS:
        return None

    if s in {"q", "quit", "exit"}:
        return s

    return int(s)


def print_menu():
    print("\n可用命令：")
    print("  1 -> 向右")
    print("  2 -> 向左")
    print("  3 -> 向下")
    print("  4 -> 向上")
    print("  0 -> 复位")
    print("  5 -> 开激光")
    print("  6 -> 关激光")
    print("  q -> 退出程序")


def main():
    sender = None
    try:
        sender = GPIOSender()
        print_menu()

        while True:
            user_input = input("\n请输入命令: ")
            command = parse_command(user_input)

            if command is None:
                print("输入无效，请输入 0~6 或 q。")
                continue

            if command in {"q", "quit", "exit"}:
                print("收到退出命令，程序结束。")
                break

            try:
                sender.send_signal(command)
            except Exception as e:
                print(f"执行命令 {command} 时出错: {e}")
                sender.safe_all_off()

    except KeyboardInterrupt:
        print("\n程序被用户中断。")
    except Exception as e:
        print(f"程序初始化或运行时发生异常: {e}")
    finally:
        if sender is not None:
            sender.close()


if __name__ == "__main__":
    main()
