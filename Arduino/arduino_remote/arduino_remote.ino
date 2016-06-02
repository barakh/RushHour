void setup() {                
  for (int i = 0; i < 14; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, HIGH);

  }
  Serial.begin(115200);
}

void loop() {
  char c;
  int pin;
  int mode;
  if (Serial.available()) {
    c = Serial.read();
    pin = 0x0f & c;
    mode = (0xf0 & c) > 0;
    digitalWrite(pin, mode);
  }
}
