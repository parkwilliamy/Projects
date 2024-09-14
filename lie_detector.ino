int green = 2;
int red = 7;
int GSR = A0;
int maxRes = 0;
int minRes = 10000;
int cycle = 0;
int buzzer = 10;
int shift;

void setup() {
  // put your setup code here, to run once:
 Serial.begin(9600);
 pinMode(red, OUTPUT);
 pinMode(green, OUTPUT);
 pinMode(buzzer, OUTPUT);
 digitalWrite(red, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly: 

  while (cycle < 150) {    
  
    if (analogRead(GSR) > maxRes) {
      maxRes = analogRead(GSR);
      
    }
    
    if (analogRead(GSR) < minRes) {
      minRes = analogRead(GSR);
      
    }
    
    cycle++;
    Serial.println(analogRead(GSR));
    delay(100);

  }

  if (cycle == 150) {
    shift = 0.85*(maxRes - minRes);
    cycle++;
  }


  if (analogRead(GSR) > (maxRes + shift)) {
   // digitalWrite(buzzer, HIGH);
    digitalWrite(red, HIGH);
    digitalWrite(green, LOW);
    delay(3000);
 //   digitalWrite(buzzer, LOW);
    delay(15000);
    digitalWrite(green, HIGH);
    digitalWrite(red, LOW);
  }

  Serial.println(analogRead(GSR));
  delay(100);

  
  
}
