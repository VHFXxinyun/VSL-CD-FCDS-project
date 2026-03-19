#include <SCServo.h>
SMS_STS st;
#define S_RXD 18
#define S_TXD 19
const int OUTPUT_PIN = 4;
byte servo_ID[2];
s16 servo_position[2];
u16 servo_speed[2];
byte servo_accels[2];

const s16 SERVO0_HOME = 2500;
const s16 SERVO1_HOME = 2400;


const s16 SERVO0_MIN = 1000;
const s16 SERVO0_MAX = 3000;


const s16 SERVO1_MIN = 1000;
const s16 SERVO1_MAX = 3000;

const int MAX_DELTA = 50;   // 单次增量限幅


// 触发输出引脚的函数
// 默认持续 1000 毫秒（1 秒）
void triggerOutput(unsigned long duration_ms = 1000) {
  digitalWrite(OUTPUT_PIN, HIGH);
  delay(duration_ms);
  digitalWrite(OUTPUT_PIN, LOW);
}

// 向树莓派发送正常确认信息
void sendAck(const String& cmd) {
  Serial.print("Received: ");
  Serial.println(cmd);

  Serial.print("OK: ");
  Serial.println(cmd);
}

// 向树莓派发送错误信息
void sendError(const String& msg) {
  Serial.print("ERR: ");
  Serial.println(msg);
}


void moveServos() {
  servo_position[0] = constrain(servo_position[0], SERVO0_MIN, SERVO0_MAX);

  servo_position[1] = constrain(servo_position[1], SERVO1_MIN, SERVO1_MAX);

  st.SyncWritePosEx(servo_ID, 2, servo_position, servo_speed, servo_accels);
}


// 检查一个字符串是否是合法的带符号整数
bool isValidSignedInteger(const String& s) {
  // 空字符串不合法
  if (s.length() == 0) {
    return false;
  }

  // 逐个字符检查
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);

    // 第 0 个字符允许是 '+' 或 '-'
    if (i == 0 && (c == '+' || c == '-')) {
      continue;
    }

    // 其他位置必须是数字
    if (!isDigit(c)) {
      return false;
    }
  }

  // 所有字符都符合要求，说明是合法带符号整数
  return true;
}


// 解析增量命令，例如：+15,-24
// 解析成功后：
// panDelta = 15
// tiltDelta = -24
bool parseIncrementCommand(const String& cmd, int& panDelta, int& tiltDelta) {
  // 找英文逗号的位置
  int commaIndex = cmd.indexOf(',');

  // 如果没有逗号，说明格式不对
  if (commaIndex == -1) {
    return false;
  }

  // 取逗号前面的部分，作为 panDelta 字符串
  String panStr = cmd.substring(0, commaIndex);

  // 取逗号后面的部分，作为 tiltDelta 字符串
  String tiltStr = cmd.substring(commaIndex + 1);

  // 去掉首尾空格
  panStr.trim();
  tiltStr.trim();

  // 检查这两部分是否都是合法带符号整数
  if (!isValidSignedInteger(panStr) || !isValidSignedInteger(tiltStr)) {
    return false;
  }

  // 转成整数
  panDelta = panStr.toInt();
  tiltDelta = tiltStr.toInt();

  return true;
}


// setup() 在上电或复位后执行一次
void setup() {
  Serial.begin(115200);
  Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD);

  st.pSerial = &Serial1;

  delay(500);

  Serial.println("ESP32 ready");
  Serial.println("Servo ready");

  servo_ID[0] = 1;
  servo_ID[1] = 2;

  servo_speed[0] = 3400;
  servo_speed[1] = 3400;

  servo_accels[0] = 50;
  servo_accels[1] = 50;

  servo_position[0] = SERVO0_HOME;
  servo_position[1] = SERVO1_HOME;

  pinMode(OUTPUT_PIN, OUTPUT);


  digitalWrite(OUTPUT_PIN, LOW);

  moveServos();

  delay(1000);
}


void loop() {
  // 如果串口里有来自树莓派的数据
  if (Serial.available()) {
    // 读取一整行，直到遇到换行符 '\n'
    String cmd = Serial.readStringUntil('\n');

    // 去掉首尾空格
    cmd.trim();

    // 把命令转成大写
    // 例如 home -> HOME
    cmd.toUpperCase();

    // 如果命令为空，就直接返回
    if (cmd.length() == 0) {
      return;

    if (cmd == "HOME") {
      // 两个舵机回到 HOME 位置
      servo_position[0] = SERVO0_HOME;
      servo_position[1] = SERVO1_HOME;

      // 执行舵机动作
      moveServos();

      // 给树莓派返回确认
      sendAck(cmd);
      return;
    }

    if (cmd == "OUT") {
      // 触发输出引脚
      triggerOutput();

      // 给树莓派返回确认
      sendAck(cmd);
      return;
    }

    // =========================
    // 增量命令解析
    // =========================

    // 先定义两个变量，用于接收解析结果
    int panDelta = 0;
    int tiltDelta = 0;

    // 尝试解析类似 +15,-24 的命令
    bool ok = parseIncrementCommand(cmd, panDelta, tiltDelta);

    // 如果解析失败，返回错误
    if (!ok) {
      sendError("INVALID_CMD");
      return;
    }

    // 对单次增量做限幅，防止一次动作太大
    panDelta = constrain(panDelta, -MAX_DELTA, MAX_DELTA);
    tiltDelta = constrain(tiltDelta, -MAX_DELTA, MAX_DELTA);

    // 根据你已经测出来的方向约定：
    // panDelta 正 -> 向右
    // panDelta 负 -> 向左
    // tiltDelta 正 -> 向下
    // tiltDelta 负 -> 向上

    // 更新水平轴位置
    servo_position[0] += panDelta;

    // 更新垂直轴位置
    servo_position[1] += tiltDelta;

    // 把新位置发送给舵机
    moveServos();

    // 给树莓派返回确认
    sendAck(cmd);
  }
}
