/* WindowC.nc - Wires interfaces needed to sample window sensor on ADC0

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



===========================
Window Sensor Wiring
===========================

Wires interfaces needed to sample Window sensor on ADC0


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  14th October 2013
*/


generic configuration WindowC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components WindowP;
  AdcReadClientC.AdcConfigure -> WindowP;
  AdcReadStreamClientC.AdcConfigure -> WindowP;
}
