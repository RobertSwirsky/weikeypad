from machine import Pin
import time
import rp2
from rp2 import PIO

# the PIO can only handle 32 bits, so we'll read one bit at a time here
# to handle arbitrary length Weigand messages
@rp2.asm_pio()
def rx_weigand():  # set_init=[PIO.IN_HIGH, PIO.IN_HIGH]
    set(x, 3)					# we will compare our pins to b'00011' if not equal, one pin is set
    label('wait_for_data')
    mov(isr, null)
    in_(pins, 2)				#read two pins
    mov(y, isr)
    jmp(x_not_y, 'bit_set')		# if it's not b'00011', then one pin is set
    mov(isr, null)				# otherwise, clear it, and read some more
    jmp('wait_for_data')		# if not, keep looking
    label('bit_set')
    push()
    label('wait_for_zero')		# now wait for them to both be clear before waiting for another bit
    mov(isr, null)
    in_(pins,2)
    mov(y,isr)
    jmp(x_not_y, 'wait_for_zero')
    jmp('wait_for_data')
    
        
# a bit is 40 microseconds wide, so we'll us a cycle rate of 10 microseconds so we
# won't miss one
pin16 = Pin(16, Pin.IN, Pin.PULL_DOWN)
pin17 = Pin(17, Pin.IN, Pin.PULL_DOWN)
sm = rp2.StateMachine(0, rx_weigand, freq=2000000, in_base=pin16)
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
        elif data == 0:
            pass
        elif data == 3:
            print(data)
            bits = bits + "?" # shouldn't ever happen
        else:
            print(data)
        if len(bits) > 100:
            break;
        # Wait for either timeout or something on the fifo
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, start_time)
        if sm.rx_fifo() > 0:
            data = sm.get()
        else:
            data = 0
        if elapsed_time > 100:
            break
    # we've time out -- that means we're at the end of a word
    print(f"Bits %s" % (bits))


