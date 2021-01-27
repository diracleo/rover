int speedPin_M1 = 5;
int speedPin_M2 = 6;
int directionPin_M1 = 4;
int directionPin_M2 = 7;
int data;
int dir;
char buffer[1];

void setup(){
  Serial.begin(9600);
}

void loop(){
  if(Serial.available()) {
    data = Serial.parseInt();
    Serial.readBytes(buffer, 1);
    powerLeft(data);
    data = Serial.parseInt(); 
    Serial.readBytes(buffer, 1);
    powerRight(data); 
  }
}

void powerLeft(int data){
  dir = LOW;
  if(data < 0) {
    data = abs(data);
    dir = HIGH;
  }
  analogWrite(speedPin_M2, data);
  digitalWrite(directionPin_M2, dir);
}

void powerRight(int data){
  dir = LOW;
  if(data < 0) {
    data = abs(data);
    dir = HIGH;
  }
  analogWrite(speedPin_M1, data);
  digitalWrite(directionPin_M1, dir);
}
