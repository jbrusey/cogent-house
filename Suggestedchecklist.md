Check list:

  1. Take with you:
    * Box with:
      1. Server +router (power supplies for each)
      1. Server node
      1. 1 air quality (AQ) node
      1. 3 CO2 nodes
      1. 1 current cost node
      1. 4 bare nodes
      1. Current Cost device
      1. 4 plugs for AQ and CO2 nodes
      1. Batteries
      1. 3 way adaptor
      1. Current cost cable
      1. USB extension
      1. Power cord extension
      1. List with node codes and room codes
    * Documentation, monitor, keyboard if needed
    * Miscellaneous equipment:
      1. Set of screwdrivers
      1. A sharp object (such as paper clip) that will fit through the reset hole of the node in case it needs resetting
      1. Cable ties for power cables for the air quality nodes and CO2 nodes.
    * Laptops (you might need a second Ethernet cable), scissors, pencil

  1. Before going into the home :
    * You will have a list with all the properties and what sensors are going in what room of the house as per example below:
|Street Name|House No.|Type Node|Room Type|ID |Date/Time|Fixed to wall tick|Producing data tick|Battery installed tick|Notes|
|:----------|:--------|:--------|:--------|:--|:--------|:-----------------|:------------------|:---------------------|:----|
|1          |26       |Bare node|Kitchen  |836|         |                  |                   |                      |     |

  1. During deployment:
    * Install servers:
      1. Plug in the router
      1. Check is functional
      1. Check with the date command all dates are synced (this should be in your documentation)
    * Install AQ/CO2 nodes:
      1. The sensors provide a way to be mounted on the wall – if you chose this option you will need a drill, and adequate screws
      1. The sensor needs to be placed on a surface (if not placed on a wall) at chest hight
        1. Away from direct sun light
        1. As far as possible from a heat source such as radiator or fridge
      1. Connect node to power supply
      1. Check that CO2 and AQ node power supply is in properly.
      1. Check that the nodes blinks
      1. Tidy cables
    * Install base nodes:
      1. Follow the same step as per AQ/CO2 installation
      1. Install batteries,
      1. Check that the nodes blinks
    * Install Current Cost nodes:
      1. The current cost devices are all labelled with the same label that the corresponding cc base node is (that does not mean that you can't use any other device than the one labelled – this was the way we use to keep the sets together)
      1. Make sure that the device is set up as Appliance 0
      1. On the transmitter hold down the button and release and you should notice that the LED flash
      1. After press the down button on the display until the LED blinks. They should be paired up.
    * Check after 5 minutes from the last sensor installed if a reading went through
      1. Go to web interface first for each type plus check the last heard time
      1. If not working:
        * for bare nodes: check battery voltage, do a reset
        * for CO2 and AQ nodes: check is the power supply is plugged in properly and reset the node
    1. Final checks after full deployment:
      * Check if data looks good
      * Confirm all nodes are up and sending data
      * Check the yield
      * Take meter readings (if you can)
      * Consolidate all notes and feedback that needs to go back to orbit.