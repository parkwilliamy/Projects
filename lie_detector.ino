int green = 2;
int red = 7;
int GSR = A0; //galvanic skin response (GSR), spikes in this number indicate lying from sweating
int maxGSR = 0; //maximum GSR, default is zero before user is hooked up to detector
int minGSR = 10000; //minimum GSR
int period = 0;
int buzzer = 10;
int avgGSR;

void setup() {
  // put your setup code here, to run once:
 Serial.begin(9600);
 pinMode(red, OUTPUT);
 pinMode(green, OUTPUT); //green LED turns on if lie isn't detected
 pinMode(buzzer, OUTPUT); //buzzer goes off if person is detected to be lying
 digitalWrite(red, HIGH); //red LED on by default
}

void loop() {
  // put your main code here, to run repeatedly: 

  while (period < 150) {  //15 second calibration period, measures the minimum and maximum skin conductivity 
  
    if (analogRead(GSR) > maxGSR) {
      maxGSR = analogRead(GSR);
      
    }
    
    if (analogRead(GSR) < minGSR) {
      minGSR = analogRead(GSR);
      
    }
    
    period++;
    Serial.println(analogRead(GSR));
    delay(100);

  }

  if (period == 150) {
    avgGSR = 0.85*(maxGSR - minGSR); //best measure of average GSR based off trial and error, reference for abnormal spikes (i.e., when someone is lying)
    period++;
  }


  if (analogRead(GSR) > (maxGSR + avgGSR)) { //if user's GSR goes above what is considered a "normal" level, the lie detector is triggered
    digitalWrite(buzzer, HIGH);
    digitalWrite(red, HIGH);
    digitalWrite(green, LOW);
    delay(3000);
    digitalWrite(green, HIGH);
    digitalWrite(red, LOW);
  }

  Serial.println(analogRead(GSR));
  delay(100);

  
  
}
