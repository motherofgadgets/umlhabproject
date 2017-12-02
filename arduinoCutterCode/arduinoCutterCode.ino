int REDPIN = 12;
int pause = 1000;
// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  int outOfBounds = 0;
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(REDPIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() 
{
  int outOfBounds = Serial.parseInt();
  if (outOfBounds > 0)
  {
    digitalWrite(LED_BUILTIN, HIGH); 
    digitalWrite(REDPIN, HIGH);
    delay(1000*10);
    digitalWrite(LED_BUILTIN, LOW); 
    digitalWrite(REDPIN, LOW);
    delay(1000*30);
    while (1)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(pause);
      digitalWrite(LED_BUILTIN, LOW);
      pause= pause - 300;
      digitalWrite(LED_BUILTIN, HIGH);
      delay(pause);
      digitalWrite(LED_BUILTIN, LOW);
      pause= pause - 300;
      digitalWrite(LED_BUILTIN, HIGH);
      delay(pause);
      digitalWrite(LED_BUILTIN, LOW);
      pause = 1000;
    }
  }
  
  
  
 
  
  
  

}
