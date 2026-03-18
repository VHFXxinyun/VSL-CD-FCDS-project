void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("ESP32 ready");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    Serial.print("Received: ");
    Serial.println(cmd);

    Serial.print("OK: ");
    Serial.println(cmd);
  }
}
