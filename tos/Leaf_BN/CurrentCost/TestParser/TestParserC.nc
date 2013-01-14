/* -*- c -*-

   Copyright (C) 2011 Ross Wilkins

   This File is part of Cogent-House

   Cogent-House is free software: you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   Cogent-House is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program. If not, see
   <http://www.gnu.org/licenses/>.

*/

#include "Parser.h"
#include "printf.h"

module TestParserC
{
  uses
    {		
      interface BigAsyncQueue<uint8_t> as MsgQueue;
      interface Parser;
      interface Boot;
      interface Leds;
    }
}
implementation
{
  //Get data method

  void printfFloat(float toBePrinted) {
    uint32_t fi, f0, f1, f2;
    char c;
    float f = toBePrinted;

    if (f<0){
      c = '-'; f = -f;
    } else {
      c = ' ';
    }

    // integer portion.
    fi = (uint32_t) f;

    // decimal portion...get index for up to 3 decimal places.
    f = f - ((float) fi);
    f0 = f*10;   f0 %= 10;
    f1 = f*100;  f1 %= 10;
    f2 = f*1000; f2 %= 10;
    printf("%c%ld.%d%d%d\n", c, fi, (uint8_t) f0, (uint8_t) f1, (uint8_t) f2);
  }




  event void Parser.onValue(char *path, char *value) {
    if (strcmp(path, "/msg/ch1/watts") == 0) {
      printf("watts is %s\n", value);
    }
    else if (strcmp(path,"/msg/tmpr") == 0) {
      printf("temp is %s\n", value);
    }
  }

  /* task void parseMessage() {  */
  /*   if (call Parser.parse() != SUCCESS) {  */
  /*     printf("couldn't parse msg: %s\n", call Parser.lastError()); */
  /*   } */
  /* } */


  char msg1[] = 
"<msg>"
"   <src>CC128-v0.11</src>     "
"   <dsb>00089</dsb>         "
"   <time>13:02:39</time>     "
"   <tmpr>18.7</tmpr>         "
"   <sensor>1</sensor>       "
"   <id>01234</id>            "
"   <type>1</type>             "
"   <ch1>                      "
"      <watts>00345</watts>    "
"   </ch1>"
"   <ch2>"
"      <watts>02151</watts>"
"   </ch2>"
"   <ch3>"
"      <watts>00000</watts>"
"   </ch3>"
    "</msg>"
"<msg>"
"   <src>CC128-v0.11</src>     "
"   <dsb>00089</dsb>         "
"   <time>13:02:39</time>     "
"   <tmpr>18.7</tmpr>         "
"   <sensor>1</sensor>       "
"   <id>01234</id>            "
"   <type>1</type>             "
"   <ch1>                      "
"      <watts>00345</watts>    "
"   </ch1>"
"   <ch2>"
"      <watts>02151</watts>"
"   </ch2>"
"   <ch3>"
"      <watts>00000</watts>"
"   </ch3>"
    "</msg>"
"\r\n<msg><tmpr>13.0</tmpr></msg>"
"\r\n<msg><d1>12.0</d2></msg>"
"<msg>"
"   <src>CC128-v0.11</src>     "
"   <dsb>00089</dsb>         "
"   <time>13:02:39</time>     "
"   <tmpr>18.7</tmpr>         "
"   <sensor>1</sensor>       "
"   <id>01234</id>            "
"   <type>1</type>             "
"   <ch1>                      "
"      <watts>00345</watts>    "
"   </ch1>"
"   <ch2>"
"      <watts>02151</watts>"
"   </ch2>"
"   <ch3>"
"      <watts>00000</watts>"
"   </ch3>"
    "</msg>"
;

  int rb_state = 0;

  task void parseMessage() {
    if (call Parser.parse() != SUCCESS) { 
      printf("error was: %s\n", call Parser.lastError());
      //printfflush();
    }
    else {
      printf("parser success\n");
      printfflush();
    }
  }

  void receiveByte(uint8_t byte, uint16_t i) {
   char emsg[] = "</msg>";
    call MsgQueue.enqueue(byte);

    // simple regexp match for .*</msg>
    if (rb_state < sizeof emsg - 1 && emsg[rb_state] == (char) byte) {
      rb_state++;
      if (rb_state == sizeof emsg - 1) {
	//call Leds.led0On();
	printf("starting parsing\n");
	printfflush();
	post parseMessage();
	//call Leds.led0Off();
	rb_state = 0;
      }
    }
    else
      rb_state = 0;
  }

  uint16_t i = 0 , j = 0 ;

  task void oneByte() { 
    if (i < strlen(msg1)) {
      receiveByte((uint8_t) msg1[i], i);
      i++;
      post oneByte();
    }
    else if (j < 3) { 
      printf("iteration %d\n", j);
      i = 0;
      j++;
      post oneByte();
    }
  }
  
  event void Boot.booted() 
  {
    post oneByte();
  }


}

