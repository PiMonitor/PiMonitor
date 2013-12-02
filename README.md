PiMonitor
=========

PiMonitor is an interface for using your RaspberryPi hardware to interface with a Subaru ECM using their SSM protocol.

Known issues:
- RPi hangs on FTDI I/O unless dwc_otg.speed=1 is set (USB 1.1 forced)

TODO - it depends on what is expected but there are two things missing in the parser that would be useful anyway:
- parse switch parameters (on/off values)
- parse ROM ID based parameters (example: front left wheel speed - it is not a PID returned by ECU but memory address - where this value is stored - is known for certain ECU ROMs)
Now PIDs returned as supported by TCU/ECU are handled and also "calculated" PIDs are handled - it is just a formula and calculation is done using real PIDs (fuel consumption for example).
