/* -*- c -*-
   ACStatusM.nc -Check the status of AC power

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
AC Status Module
=====================================

The module check the status of powered nodes to see if they are AC or battery powered

:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  09/05/2013
*/


generic module ACStatusM()
{
  provides {
    interface Read<bool> as ReadAC;
    interface StdControl as ACControl;
  }
  uses {	
    interface HplMsp430GeneralIO as ACInput;
  }
}
implementation
{ 
  bool has_started = FALSE;

  task void readTask() {
    bool state;
    state = call ACInput.get();
    signal ReadAC.readDone(SUCCESS, state);
  }

  command error_t ReadAC.read() {
    if (has_started) {
      post readTask();
      return SUCCESS;
    }
    else
      return FAIL;
  }
  
  command error_t ACControl.start() {
    call ACInput.makeInput();
    has_started = TRUE;
    return SUCCESS;
  }
  
  command error_t ACControl.stop() {
    has_started = FALSE;
    return SUCCESS;
  }
       
}

