from machine import Pin, Timer
import time
import rp2
from rp2 import PIO
      
if __name__ == "__main__":
    from machine import Pin
import time

    # List of GPIO pins available on the RP2040 (0–28)
    # Skip pins reserved for flash or special functions as needed.
    gpio_pins = list(range(29))

    # Prepare an array of pin objects configured as inputs
    pins = []
    for i in gpio_pins:
        try:
            p = Pin(i, Pin.IN, Pin.PULL_DOWN)
            pins.append((i, p))
        except:
            # Ignore invalid or unavailable pins
            pass

    # Main loop: read and print pin states repeatedly
    while True:
        states = []
        for i, p in pins:
            val = p.value()
            states.append(str(val))
        print("".join(states))
        time.sleep(0.5)


              
        


