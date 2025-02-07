from machine import Pin
import time
import rp2
from rp2 import PIO

# the PIO can only handle 32 bits, so we'll read one bit at a time here
# to handle arbitrary length Weigand messages
@rp2.asm_pio(set_init=PIO.IN_HIGH)
def rx_weigand():
    set(x, 11)					# we will compare our pins to b'00011' if not equal, one pin is set
    label('wait_for_data')
    in_(pins, 2)				#read two pins
    mov(y, isr)
    jmp(x_not_y, 'bit_set')		# if it's not b'00011', then one pin is set
    jmp('wait_for_data')		# if not, keep looking
    label('bit_set')
    push()
    jmp('wait_for_data')
    
        
# a bit is 40 microseconds wide, so we'll us a cycle rate of 10 microseconds so we
# won't miss one
pin0 = Pin(0, Pin.IN, Pin.PULL_DOWN)
sm = rp2.StateMachine(0, rx_weigand, freq=100000, in_base=pin0)
sm.active(1)

while True:
    bits = ""
    print("Waiting for a word")
    data = sm.get()				# wait for a bit detected from the FIFO
    start_time = time.ticks_ms()
    elapsed_time = 0
    while True:
        if data == 1:
            bits = bits + "1"
        elif data == 2:
            bits = bits + "0"
        else:
            bits = bits + "?"
        # Wait for either next bit or something on the fifo
        while (sm.rx_fifo() == 0):
            current_time = time.ticks_ms()
            elapsed_time = time.ticks_diff(current_time, start_time))
            if elapsed_time > 5:
                break
        # check to see if we're here because of something in fifo or timeout
        if elapsed_time > 5:
            break			# timeout. We're done
        data = sm.get()
    # we've time out -- that means we're at the end of a word
    print(f"Bits %s" % (bits))

