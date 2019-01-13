# sainsmart
Python controller for Sainsmart USB Relay SKU: 101-70-208 / QinHeng Electronics HL-340 USB-Serial adapter

Note: 
Some of the Sainsmart 16-channel relays have a HID compatible chip.  This one is a QunHeng Electronics HL-340 USB Serial adapter.  You can see the difference when you plug the USB cable in and (on linux) type 'lsusb' at the command prompt.


SKU: 101-70-208


Overall good:

    Low price
    16 channels 1 board
    No 'daughter board' for the USB host module


Overall bad:

    -No HID compatible software support, no provided drivers for linux, very little documentation
    -The status command doesn't return anything, which I think would be a key software feature is to check what we think the relay is doing with what the board says the relay is doing.
    -One of the board makes a whining noise when contact is closed
    -KILLER:  there is no hardware level serial number, which means we can't really guarantee we can keep multiple boards addressed properly over time.  There are potentially ways around them, but none of them come without cost and complexity.
    -No 'plug style' 12v power in like the Knacro.  You have to put in a spliced power chord into screw terminals.


What was learned in the process:

    -You have to set permissions in /etc/dev/rules.d in order for a non-root user to configure a device.
    -You have to drop the kernel driver off the card in order to configure it in python.
    -Having a serial number in the usb.core.get_active_configuration board return info would allow you to address by serial number
    -Still struggling occasionally with some error on 'resource busy' — that may be helped by a better board that can return a status
    -You can send separate serial commands pretty fast.  Even though you have to send individual relay commands separately, it is almost indistinguishable
    -If encoded as a string literal, pyusb likes a format with slashes in it.  I think it is best to store commands as tuples of decimal value ints and send like that.
    -Python 3 converted hex characters automatically to integer value decimals.  The board took both, but there are potential for errors because a hex value provided by sainsmart (0x0A stripping the 0x) that looks like 0A would be imported as a string and 0x30 would be imported as an int and sometimes as a float.  Then the float creates other problems for string parsing.

# How to use it: 
1. You may need to install certain dependencies and/or libraries for pyusb (YMMV)

2. The hex commands from the Sainsmart wiki page are converted to decimals and in an indexed list.

3. The format for indexing the control serial messages is: 
Relay Number X 2 = turn on that relay
Relay Number X 2 + 1 = turn off that relay

For example, 
> ep.write(ss_cont[12])     # turns off relay number 6
> ep.write(ss_cont[13])     # would turn off relay number 6  



