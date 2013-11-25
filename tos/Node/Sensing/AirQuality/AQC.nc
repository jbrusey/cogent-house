/* CarbonDioxideP.nc - Wires interfaces needed to sample AQ sensor on ADC0

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
AQ Wiring
===========================

Wires interfaces needed to sample AQ sensor on ADC0


:author: Ross Wilkins
:email: ross.wilkins87@googlemail.com
:date:  6th January 2011
*/

generic configuration AQC() {
  provides interface Read<uint16_t>;
  provides interface ReadStream<uint16_t>;
}
implementation {
  components new AdcReadClientC();
  Read = AdcReadClientC;

  components new AdcReadStreamClientC();
  ReadStream = AdcReadStreamClientC;

  components AQP;
  AdcReadClientC.AdcConfigure -> AQP;
  AdcReadStreamClientC.AdcConfigure -> AQP;
}
