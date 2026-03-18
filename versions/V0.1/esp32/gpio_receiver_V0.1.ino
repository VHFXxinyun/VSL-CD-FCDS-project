#include <SCServo.h>  // 包含SCServo库，用于控制ST系列伺服电机

SMS_STS st;  // 创建一个SMS_STS对象，用于与伺服电机通信和控制

// 用于控制伺服电机的串口
// 默认使用 GPIO 18 - S_RXD, GPIO 19 - S_TXD
#define S_RXD 18  // 定义接收引脚为GPIO 18
#define S_TXD 19  // 定义发送引脚为GPIO 19

const int recvPin_1 = 16; //设置GPIO5（树莓派17）
const int recvPin_2 = 27; //设置GPIO4（树莓派18）
const int recvPin_3 = 5; //设置GPIO5（树莓派13）
const int recvPin_4 = 4; //设置GPIO4（树莓派15）  

byte ID[2];  // 定义伺服电机ID数组，用于存储两个伺服电机的ID
s16 Position[2];  // 定义位置数组，用于存储两个伺服电机的位置
u16 Speed[2];  // 定义速度数组，用于存储两个伺服电机的速度
byte ACC[2];  // 定义加速度数组，用于存储两个伺服电机的加速度
void setup()  // 初始化函数，在设备上电或复位后运行一次
{
  Serial.begin(115200);  // 初始化串口通信，波特率115200，用于调试输出
  Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD);  // 初始化Serial1用于伺服电机通信，波特率1000000，使用指定引脚
  st.pSerial = &Serial1;  // 将Serial1设置为伺服电机对象的通信端口
  
  delay(1000);  // 延迟1秒，等待系统稳定和初始化完成 
  
  ID[0] = 1;  // 设置第一个伺服电机的ID为1
  ID[1] = 2;  // 设置第二个伺服电机的ID为2
  Speed[0] = 3400;  // 设置第一个伺服电机的速度为3400
  Speed[1] = 3400;  // 设置第二个伺服电机的速度为3400
  ACC[0] = 50;  // 设置第一个伺服电机的加速度为50
  ACC[1] = 50;  // 设置第二个伺服电机的加速度为50
  Position[0] = 2500;  // 设置第一个伺服电机的目标位置为3000
  Position[1] = 2000;  // 设置第二个伺服电机的目标位置为3000
  st.SyncWritePosEx(ID, 2, Position, Speed, ACC);  // 同步写入位置、速度和加速度，使两个伺服电机同时移动到指定位置
  
  delay(1000);  // 延迟1秒，等待伺服电机完成运动    
  
  pinMode(recvPin_1, INPUT); // 将引脚1设置为输入模式
  pinMode(recvPin_2, INPUT); // 将引脚2设置为输入模式
  pinMode(recvPin_3, INPUT); // 将引脚3设置为输入模式
  pinMode(recvPin_4, INPUT); // 将引脚4设置为输入模式
  Serial.println("ESP32 接收器就绪，正在监听 GPIO5&4&27&16...");
  delay(1500);
}

void loop()  // 主循环函数，重复执行其中的代码
{
  int signalState_1 = digitalRead(recvPin_1); // 读取引脚电平
  int signalState_2 = digitalRead(recvPin_2);
  int signalState_3 = digitalRead(recvPin_3); // 读取引脚电平
  int signalState_4 = digitalRead(recvPin_4);
  if (signalState_1 == HIGH) {
    Serial.println("收到信号: HIGH1 (3.3V)");
    Position[0] = Position[0] + 100;
  } else {
    Serial.println("收到信号: LOW1 (0V)");
  }
  
  if (signalState_2 == HIGH) {
    Serial.println("收到信号: HIGH2 (3.3V)");
    Position[0] = Position[0] - 100;
  } else {
    Serial.println("收到信号: LOW2 (0V)");
  }
  
  if (signalState_3 == HIGH) {
    Serial.println("收到信号: HIGH3 (3.3V)");
    Position[1] = Position[1] + 100;
  } else {
    Serial.println("收到信号: LOW3 (0V)");
  }

  if (signalState_4 == HIGH) {
    Serial.println("收到信号: HIGH4 (3.3V)");
    Position[1] = Position[1] - 100;
  } else {
    Serial.println("收到信号: LOW4 (0V)");
  }
  if (signalState_1 == HIGH && signalState_2 == HIGH) {
    Serial.println("收到复位信号");
    Position[0] = 2500;
    Position[1] = 2000;
  }

  st.SyncWritePosEx(ID, 2, Position, Speed, ACC);  // 同步写入位置、速度和加速度，使两个伺服电机同时移动到指定位置
  delay(100); // 每100毫秒检查一次，可根据需要调整
}
