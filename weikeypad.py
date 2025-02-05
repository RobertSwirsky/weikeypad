import rp2
from machine import Pin
import time

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT, autopush=True, push_thresh=32)
def wiegand_pio():
    wait(0, pin, 0)  # Wait for DATA0 to go low
    in_(pins, 1)     # Shift in 1 bit from DATA0
    wait(1, pin, 0)  # Wait for DATA0 to go high
    wait(0, pin, 1)  # Wait for DATA1 to go low
    in_(pins, 1)     # Shift in 1 bit from DATA1
    wait(1, pin, 1)  # Wait for DATA1 to go high

# Set up the state machine
sm = rp2.StateMachine(0, wiegand_pio, freq=10000, in_base=Pin(2))

# Enable the state machine
sm.active(1)

def decode_wiegand(data, bits):
    if bits == 26:
        facility = (data >> 17) & 0xFF
        card_number = data & 0xFFFF
        return facility, card_number
    elif bits == 34:
        card_number = data & 0xFFFFFFFF
        return None, card_number
    else:
        return None, None

# Main loop
while True:
    if sm.rx_fifo():
        data = sm.get()
        bits = 32  # Assuming 32-bit Wiegand data
        facility, card_number = decode_wiegand(data, bits)
        if card_number is not None:
            print(f"Facility: {facility}, Card Number: {card_number}")
    time.sleep(0.1)
