/*
  arduinoCutterCode

  Reads the serial connection. When a signal higher than 0 is received,
  Initiates cutter sequence

  written August 2017
  by Alex Hernandez and Russell Perkins
  modified 1 Dec 2017
  by Danae Moss
*/

int REDPIN = 12;
int pause = 1000;
// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  int outOfBounds = 0;
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT); //built-in light
  pinMode(REDPIN, OUTPUT); // Pin for cutter current
}

// the loop function runs over and over again forever
void loop() 
{
  int outOfBounds = Serial.parseInt(); //Get message from serial connection
  if (outOfBounds > 0) // If message > 0, initiate cutting
  {
    digitalWrite(LED_BUILTIN, HIGH); 
    digitalWrite(REDPIN, HIGH); //send high current to cutter wire
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
