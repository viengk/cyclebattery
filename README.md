# Cycle Battery

This program cycles a battery for testing purposes using a Rigol DP811 power supply and Rigol DL3031 electronic 
load.

## Installation

1. Download and install Ultra Sigma software which is available on Rigol's website

2. Download and install Python 3. During installation, allow python to be run from command prompt. Make sure pip 
gets installed.

3. Install pyvisa library using pip

```
pip install pyvisa
```
4. Download the latest code from https://github.com/phufford/cyclebattery, click "Clone or Download", download 
as zip, then unzip. 

## Use

Turning on "Sense" programmatically does not work for some electronic loads. Make sure sense is on before 
running

Double click cycle_battery.bat to run. Choose the cycle settings you want to use as defined in config.ini

To stop cycling battery hold "Ctrl" and press c

Cycle profiles can be modified in config.ini file. DEFAULT must always be included with all settings options 
specified. Different charging profile options can be added which override the defult. If settings are not 
specified in attitional charging profile options, the setting defined in DEFULT will be used.

## License

This project is licensed under the MIT License - see the LICENCE.txt file for details
