#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>

#define BUF_SIZ 20;

hd44780_I2Cexp lcd;
String s;
byte b[80];
int i;
int j;
byte v;
int ready;

void setup() 
{
  Serial.begin(9600);  
  lcd.begin(20,4);
  lcd.print(".");
}

void loop() 
{
  // Serial has a buffer of 64 bytes, but our display
  // uses 80. So the python code sends a 2 (STX)
  // followed by the bytes to print on the LCD, and
  // capped-off with a 3 (ETX) which is our cue to
  // actually send the (complete) data to the LCD.
  while (Serial.available())
	{
		v = Serial.read();
    if(v == 2) 
    {
      // Start of Text
      i = 0;
    }
    else if(v == 3) 
    {
      // end of Text
      ready = 1;
    }
    else if(i < 80)
    {
      // body
      b[i] = v;
      i++;
    }
	}
 
  if(ready == 1) 
  {
    j = 0;
    lcd.clear();
    while(j < i) 
    {
      lcd.write(b[j]);
      j++;
    } 
    ready = 0;   
  }
}
