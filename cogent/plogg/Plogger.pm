package Plogger;

#    Plogger.pm : a library that can make sense of part of the Plogg
#    http://www.plogginternational.com/ binary protocol.
#
#    Copyright (C) 2010  Owen Williams williams@dmu.ac.uk
#    De Montfort University
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

use Net::Telnet;
use Date::Manip;
use Getopt::Long;

sub yvAPlogg
{
  my $telnet = shift;
  my $device = shift;

  $telnet->print("AT+UCAST:$device=yv");

  my $result  = "";
  my $result2 = "";
  my $nothing = "";
  my $data    = "";

  ($nothing, $result) = $telnet->waitfor(Match => "/UCAST:.*,[a-z0-9][a-z0-9]=.*\n/", Errmode => 'return', Timeout => 5);

  unless ($result)
  {
    print STDERR "yvAPlogg 1 : $device : Nothing returned.\n";
    return;
  }

  my $length;

  if ($result =~ m/.*$device,([a-z0-9][a-z0-9])=/)
  {
    $length = hex($1);
  }

  $result =~ s/.*$device,([a-z0-9][a-z0-9])=//;

  while ($length > length($result))
  {
    ($nothing, $result2) = $telnet->waitfor(Match => "/.*\n/", Errmode => 'return', Timeout => 5);

    unless ($result2)
    {
      print STDERR "yvAPlogg 2 : $device : Nothing returned.\n";
      return;
    }

    $result .= $result2;
  }

#my $hexxy = "";
#for (my $n = 0; $n < $length; $n++)
#{
#  $hexxy .= "H2";
#}
#
#@arry = unpack($hexxy, $result);
#
#for (my $a = 0; $a <= $#arry; $a++)
#{
#  printf("%4s", $arry[$a] . "|");
#}
#
#print "\n";
#
#for (my $a = 0; $a <= $#arry; $a++)
#{
#  printf("%4s", hex($arry[$a]) . "|");
#}
#
#print "\n";

  my $length;

  if ($result =~ m/.*$device,(.*)=/)
  {
    $length = $1;
  }

  #print $length . "\n";

  $line =  $result;
  chomp($line);
  $line =~ s/UCAST.*$device,..=//;

  my @data = unpack("H2H4H4H4H8H8H8H8H8H8H8H8H8H8H8H8", $line);

  return @data;
}

sub findPloggs
{
  my $telnet = shift;

  my @ffd;

  $telnet->print("AT+SN");

  my $nothing = "";
  my $ffdId   = "";
  my $ffds    = 0;

  ($nothing, $ffdId) = $telnet->waitfor(Match => "/FFD:................/", Errmode => 'return', Timeout => 10);

  while ($ffdId)
  {
    $ffdId =~ s/FFD://;
    $ffd[$ffds++] = $ffdId;

    ($nothing, $ffdId) = $telnet->waitfor(Match => "/FFD:................/", Errmode => 'return', Timeout => 10);
  }

  return @ffd;
}

sub humanOutput
{
  my $device = shift;
  my @data   = @_;

  print "Device : $device\n";

  print "0.  Packet Count   : " . $data[0] . " " . hex($data[0]) . "\n";
  print "1.  Plogg Time     : " . $data[2] . " " . $data[3] . " " . sprintf("%02d/%02d/%02d", returnPloggDate(hex($data[2]))) .
                                                            " " . sprintf("%02d:%02d:%02d", returnPloggTime(hex($data[2]), hex($data[3]))) . "\n";
  print "2.  Watts          : " . $data[4] . " " . (hex($data[4])/1000) . " W\n";
  print "3.  kWh Generated  : " . $data[5] . " " . (hex($data[5])/10000) . " kWh\n";
  print "4.  kWh Consumed   : " . $data[6] . " " . (hex($data[6])/10000) . " kWh\n";
  print "5.  Frequency      : " . $data[7] . " " . (hex($data[7])/10) . " Hz\n";
  print "6.  RMS Voltage    : " . $data[8] . " " . (hex($data[8])/1000) . " V\n";
  print "7.  RMS Current    : " . $data[9] . " " . (hex($data[9])/1000) . " A\n";
  print "8.  Plogg up time  : " . $data[10] . " " . sprintf("%d days %d hours %d minutes %d seconds", returnDaysHoursMinutesSeconds(hex($data[10])/100)) . "\n";   ## dunno
  print "9.  Reactive Power : " . $data[11] . " " . signer($data[11])/1000 . " VAR\n";  
  print "10. VARh Generated : " . $data[12] . " " . hex($data[12]) . " KVARh\n";
  print "11. VARh Consumed  : " . $data[13] . " " . hex($data[13]) . " KVARh\n";
  print "12. Phase Angle    : " . $data[14] . " " . hex($data[14]) . " degrees\n";
  print "13. Equip up time  : " . $data[15] . " " . sprintf("%d days %d hours %d minutes %d seconds", returnDaysHoursMinutesSeconds(hex($data[15])/100)) . "\n";
  print "\n";
}

sub arrayOutput
{
  my $device = shift;
  my @data   = @_;

  my $packetCount = hex($data[0]);

  my @ploggDate   = returnPloggDate(hex($data[2]));
  my $ploggYear   = $ploggDate[0];
  my $ploggMonth  = $ploggDate[1];
  my $ploggDay    = $ploggDate[2];

  my @ploggTime   = returnPloggTime(hex($data[2]), hex($data[3]));
  my $ploggHour   = $ploggTime[0];
  my $ploggMinute = $ploggTime[1];
  my $ploggSecond = $ploggTime[2];

  my $watts       = hex($data[4]);
  my $kWhGenerated = hex($data[5]);
  my $kWhConsumed = hex($data[6]);
  my $frequency = hex($data[7]);
  my $rmsVoltage = hex($data[8]);
  my $rmsCurrent = hex($data[9]);

  my $ploggUptime        = hex($data[10]);

  my $reactivePower = signer($data[11]);
  my $varHGenerated = hex($data[12]);
  my $varHConsumed = hex($data[13]);
  my $phaseAngle = hex($data[14]);

  my $equipmentUptime        = hex($data[15]);

  return ($device, $packetCount, "$ploggYear/$ploggMonth/$ploggDay $ploggHour:$ploggMinute:$ploggSecond",
          $watts, $kWhGenerated, $kWhConsumed, $frequency, $rmsVoltage, $rmsCurrent, $ploggUptime,
          $reactivePower, $varHGenerated, $varHConsumed, $phaseAngle, $equipmentUptime);
}

sub xmlOutput
{
  my $device = shift;
  my @data   = @_;

  my $packetCount = hex($data[0]);

  my @ploggDate   = returnPloggDate(hex($data[2]));
  my $ploggYear   = $ploggDate[0];
  my $ploggMonth  = $ploggDate[1];
  my $ploggDay    = $ploggDate[2];

  my @ploggTime   = returnPloggTime(hex($data[2]), hex($data[3]));
  my $ploggHour   = $ploggTime[0];
  my $ploggMinute = $ploggTime[1];
  my $ploggSecond = $ploggTime[2];

  my $watts       = hex($data[4]);
  my $kWhGenerated = hex($data[5]);
  my $kWhConsumed = hex($data[6]);
  my $frequency = hex($data[7]);
  my $rmsVoltage = hex($data[8]);
  my $rmsCurrent = hex($data[9]);

  my @ploggUptime        = returnDaysHoursMinutesSeconds(hex($data[10])/100);
  my $ploggUptimeDays    = $ploggUptime[0];
  my $ploggUptimeHours   = $ploggUptime[1];
  my $ploggUptimeMinutes = $ploggUptime[2];
  my $ploggUptimeSeconds = $ploggUptime[3];

  my $reactivePower = signer($data[11]);
  my $varHGenerated = hex($data[12]);
  my $varHConsumed = hex($data[13]);
  my $phaseAngle = hex($data[14]);

  my @equipmentUptime        = returnDaysHoursMinutesSeconds(hex($data[15])/100);
  my $equipmentUptimeDays    = $equipmentUptime[0];
  my $equipmentUptimeHours   = $equipmentUptime[1];
  my $equipmentUptimeMinutes = $equipmentUptime[2];
  my $equipmentUptimeSeconds = $equipmentUptime[3];

print <<END;
  <plogg device="$device">
    <packetCount>$packetCount</packetCount>
    <ploggDateTime>
      <year>$ploggYear</year>
      <month>$ploggMonth</month>
      <day>$ploggDay</day>
      <hour>$ploggHour</hour>
      <minute>$ploggMinute</minute>
      <second>$ploggSecond</second>
    </ploggDateTime>
    <watts>$watts</watts>
    <kWhGenerated>$kWhGenerated</kWhGenerated>
    <kWhConsumed>$kWhConsumed</kWhConsumed>
    <frequency>$frequency</frequency>
    <rmsVoltage>$rmsVoltage</rmsVoltage>
    <rmsCurrent>$rmsCurrent</rmsCurrent>
    <ploggUptime>
      <days>$ploggUptimeDays</days>
      <hours>$ploggUptimeHours</hours>
      <minutes>$ploggUptimeMinutes</minutes>
      <seconds>$ploggUptimeSeconds</seconds>
    </ploggUptime>
    <reactivePower>$reactivePower</reactivePower>
    <varHGenerated>$varHGenerated</varHGenerated>
    <varHConsumed>$varHConsumed</varHConsumed>
    <phaseAngle>$phaseAngle</phaseAngle>
    <equipmentUptime>
      <days>$equipmentUptimeDays</days>
      <hours>$equipmentUptimeHours</hours>
      <minutes>$equipmentUptimeMinutes</minutes>
      <seconds>$equipmentUptimeSeconds</seconds>
    </equipmentUptime>
  </plogg>
END
}

sub signer
{
  my $decimal = hex($_[0]);

  return ($decimal >> 31) ? -1*($decimal^(1<<31)) : $decimal;
}

sub returnDaysHoursMinutesSeconds
{
  my @parts = gmtime(shift);
  return @parts[7,2,1,0];
}

sub returnPloggTime
{
  my $b16  = $_[0]&1;
  my $time = $_[1];

  my $secondsBitmask = 63;
  my $minutesBitmask = $secondsBitmask<<6;
  my $hoursBitmask   = $secondsBitmask<<12;

  my $seconds = $time&$secondsBitmask;
  my $minutes = ($time&$minutesBitmask)>>6;
  my $hours   = (16*$b16)+(($time&$hoursBitmask)>>12);

  return ($hours, $minutes, $seconds);
}

sub returnPloggDate
{
  # 00000000000000000000010000000000
  # 0000000000000000 00001 00001 00001 0
  my $date = $_[0];
  $date = $date>>1;
#print unpack("B32", pack("N", "" . $date)) . "\n";

  my $dayBitmask = 31;
  my $monthBitmask = 15<<5;
  my $yearBitmask = 127<<9;

  my $day   = 1+($date&$dayBitmask);
  my $month = 1+(($date&$monthBitmask)>>5);
  my $year  = ($date&$yearBitmask)>>9;

  return ($year+2000, $month, $day);
}

sub setDateTime
{
  my $device = shift;
  my $telnet = shift;

  my @localtime = localtime();

  my $date = sprintf("%d.%d.%d", $localtime[5]-100, $localtime[4]+1, $localtime[3]);
  my $time = sprintf("%d.%d.%d", $localtime[2], $localtime[1]+1, $localtime[0]);

  $telnet->print("AT+UCAST:$device=RTT$time");
  $telnet->print("AT+UCAST:$device=RTD$date");
}

1;
