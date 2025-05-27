#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>

#define BUF_SIZ 20;

hd44780_I2Cexp lcd;
String s;
byte b[20];
int i;

void setup() {
  Serial.begin(9600);
  
  lcd.begin(20,4);
  lcd.print(".");
}

void loop() {
  // wait for comms to be established
  while(!Serial.available());

  while(true) 
  {
    s = Serial.readStringUntil('\0');

    // I can likely make this much simpler by just having the python code send
    // 80 bytes each time (to fill the 20x4 screen). But my first attempts ran into wrapping
    // and truncation issues. That was before I switched to the hd44780 library, though.
    if(s == "!1")
    {
      lcd.setCursor(0,0);
    }
    else if(s == "!2") 
    {
      lcd.setCursor(0,1);
    }
    else if(s == "!3") 
    {
      lcd.setCursor(0,2);
    }
    else if(s == "!4") 
    {
      lcd.setCursor(0,3);      
    }
    else 
    {
      lcd.print(s);
    }
  }
}
