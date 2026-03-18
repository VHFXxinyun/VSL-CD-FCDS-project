from gpiozero import DigitalOutputDevice
import time

# 使用BCM引脚编号
send_pin_1 = 17  
send_pin_2 = 18  
send_pin_3 = 27
send_pin_4 = 22

# 创建两个数字输出设备，初始为低电平
output_pin_1 = DigitalOutputDevice(send_pin_1, active_high=True, initial_value=False)
output_pin_2 = DigitalOutputDevice(send_pin_2, active_high=True, initial_value=False)
output_pin_3 = DigitalOutputDevice(send_pin_3, active_high=True, initial_value=False)
output_pin_4 = DigitalOutputDevice(send_pin_4, active_high=True, initial_value=False)
print("树莓派发送器就绪。按 Ctrl+C 退出。")

try:
    while True:
        num = int(input("向右按1,向左按2,向下按3,向上按4,按0复位:"))
        print("输入脉冲次数")
        if num == 1:
            sum = int(input())
            for i in range(sum):

                output_pin_1.on()
                print("输出HIGH1")
                time.sleep(0.1)  # 保持0.1秒
                output_pin_1.off()
        if num == 2:
            sum = int(input())
            for i in range(sum):

                output_pin_2.on()
                print("输出HIGH1")
                time.sleep(0.1)  # 保持0.1秒
                output_pin_2.off()
        if num == 3:
            sum = int(input())
            for i in range(sum):

                output_pin_3.on()
                print("输出HIGH1")
                time.sleep(0.1)  # 保持0.1秒
                output_pin_3.off()
        if num == 4:
            sum = int(input())
            for i in range(sum):

                output_pin_4.on()
                print("输出HIGH1")
                time.sleep(0.1)  # 保持0.1秒
                output_pin_4.off()
        if num == 0:
            output_pin_1.on()
            output_pin_2.on()
            print("复位")
            time.sleep(0.1)  # 保持0.1秒
            output_pin_1.off()
            output_pin_2.off()


except KeyboardInterrupt:
    print("\n程序被用户中断。")

finally:
    # 关闭引脚，释放资源
    output_pin_1.off()
    output_pin_1.close()
    output_pin_2.off()
    output_pin_2.close()
    output_pin_3.off()
    output_pin_3.close()
    output_pin_4.off()
    output_pin_4.close()
    print("GPIO已清理。")
