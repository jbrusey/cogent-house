/* -*- c -*-
   WindowM.nc -Check the status of Window sensor

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



=====================================
Window Status Module
=====================================

The module check the status the Window sensor

:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  22/04/2014
*/


generic module WindowM()
{
  provides {
    interface Read<float> as ReadWindow;
    interface StdControl as WindowControl;
  }
  uses {	
    interface HplMsp430GeneralIO as WindowInput;
  }
}
implementation
{ 
  bool has_started = FALSE;

  task void readTask() {
    float state;
    if (has_started) {
      state = (float) call WindowInput.get();
      signal ReadWindow.readDone(SUCCESS, state);
    }
    else
      signal ReadWindow.readDone(FAIL, 0.f);
  }

  command error_t ReadWindow.read() {
    post readTask();
    return SUCCESS;
  }
  
  command error_t WindowControl.start() {
    call WindowInput.makeInput();
    has_started = TRUE;
    return SUCCESS;
  }
  
  command error_t WindowControl.stop() {
    has_started = FALSE;
    return SUCCESS;
  }
       
}

