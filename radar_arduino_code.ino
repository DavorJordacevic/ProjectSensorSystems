// ukljucujemo biblioteku Servo.h
#include <Servo.h>
// definisemo instancu klase Servo
Servo servo;
// definisemo sta ce se nalaziti na kom pinu
int pos=0,number=0;
int trigg=8,echo=7;
// brzina zvuka iznosti 343m/s, odnosno 0.034 cm/us
const float speed_of_sound=0.034;

void setup() {
  pinMode(trigg,OUTPUT);
  pinMode(echo,INPUT);
  // povezujemo pin 9 sa servo motorom
  servo.attach(9);
  // bitno je podesiti serijski port preko koga ce se u pythonu citati vrednosti
  Serial.begin(9600);
}

// Racunanje daljine od senzora
 float distance(){
  unsigned long duration; 
  float _distance;
  // ugasimo trigger pin
  digitalWrite(trigg,LOW);
  delayMicroseconds(2);
  // ukljucujemo trigger pin i saljemo ultrazvuk u trajanju od 10us
  digitalWrite(trigg,OUTPUT);
  delayMicroseconds(10);
  // nakon cega gasimo trigger
  digitalWrite(trigg,LOW);
  // zvuk koji se odbije od detektovanog objekta je potrebno primiti preko ehco pina
  duration=pulseIn(echo,HIGH);
  // daljinu od detektovanog objekta dobijemo tako sto ukupno vreme pomnozimo sa brzinom
  // zvuka i podelimo sa 2, jer je putanja bila duplirana
  _distance=duration*speed_of_sound/2;
  return(_distance);
}

void loop() {
  int angle;
  float _distance;
  // servo motor i senzor ce rotirati od 0 do 179 stepeni i u svakom trenutku je potrebno ocitati trenutno stanje
  for(angle=0;angle<=180;angle++){
    servo.write(angle);
    _distance=distance();
    Serial.print(angle);
    Serial.print(";");
    Serial.println(_distance);
    delay(50);
  }
  // servo motor i senzor ce rotirati od 179 do 0 stepeni i u svakom trenutku je potrebno ocitati trenutno stanje
  for(angle=180;angle>=0;angle--){
    servo.write(angle);
    _distance=distance();
    Serial.print(angle);
    Serial.print(";");
    Serial.println(_distance);
    delay(50);
  }
}
