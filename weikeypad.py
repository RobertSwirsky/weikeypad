from machine import Pin
import time
import rp2
from rp2 import PIO

#37 bit weigand format
# bits are 40 microseconds wide
# bits are 2 ms apart

# bit 1     - even parity 
# bit 2-15  - Facility Code / Site ID
# bit 16-36 - Card Id / Serial Number
# bit 37    - Odd Parity 

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
    
@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def tx_weigand():
     set(pins, 3)
     wrap_target()
     pull(block)             # 1
     mov(x, osr)             # 1
     jmp(not_x, "zero")      # 1
     set(pins,2)             # 1  zero pin low, one pin high 
     nop()        [3]        # 3
     jmp('wait2ms')          # 1 wait 2 milliseconds
     label('zero')
     set(pins, 1)            # 1 set zero pin high, one pin low
     nop()        [3]        # 3
     label('wait2ms')        # 20 x 10 = 200 x 10 microseconds = 2 milliseconds
     set(pins, 3)            # both pins high
     set(x, 19)              # 1
     label("loop")
     nop() [8]               # 
     jmp(x_dec, "loop")      # 1
     wrap()
   
class WeigandTranslator:
    def __init__(self):
        # a bit is 40 microseconds wide, so we'll us a cycle rate of 1/2 microsecond for receiving
        # so we won't won't miss one. We may be able to slow this down
        pin16 = Pin(16, Pin.IN, Pin.PULL_DOWN)
        pin17 = Pin(17, Pin.IN, Pin.PULL_DOWN)
        # start on PIO 0
        self.sm = rp2.StateMachine(0, rx_weigand, freq=2000000, in_base=pin16)
        self.sm.active(1)
        self.accumulatedBits = 0
        self.accumulatedCount = 0
        
        # for the transmit side, we will make the clock cycle rate 10 microseconds
        # so 4 cycles = 1 bit width
        pin14 = Pin(12, Pin.OUT)
        pin15 = Pin(13, Pin.OUT)
        # start on PIO 1
        self.smx = rp2.StateMachine(4, tx_weigand, freq=100000, set_base=Pin(12))
        self.smx.active(1)
        
    
    def Transmit(self, bits):
        print(f"Transmit (%d) bits: %s" % (len(bits), bits))
        for b in bits:
            # this blocks until space available, so no need to worry
            # about overflow
            self.smx.put(0 if b=='0' else 1)
        # sleep a millisecond 
        time.sleep(0.1)
        
    def AccumulateBits(self, bits):
        value = int(bits, 2)
        if value > 9:
            # we've got a * or a # - stop accumulating
            return False
        else:
            self.accumulatedBits = (self.accumulatedBits * 10) + value
            self.accumulatedCount = self.accumulatedCount + 1
            if self.accumulatedCount >= 6:
                return False
        return True
               
    def GetAccumulatedBits(self):
        # shift it right one more to make room for checksum
        a = self.accumulatedBits * 2
        self.accumulatedBits = 0
        self.accumulatedCount = 0
        bits = (bin(a))[2:]
        if len(bits) < 37:
            zerosNeeded = 37 - len(bits)
            bits = '0' * zerosNeeded + bits
        return bits
    
    def CalculateParity(self, bits):
        value = int(bits[:-1], 2)                # don't look at the last bit when calculating value
        print(f"Value = %s" % (hex(value)))
        a = bits[1:18].count('1')
        parity_front = a % 2
        b = bits[18:36].count('1') + 1
        parity_back = b % 2
        print(f"Parity bits should be %d and %d" % (parity_front, parity_back))
        if parity_front == 1:
            bits = '1' + bits[1:]
        if parity_back == 1:
            bits = bits[:-1] + '1'
        return bits    
    
    def Receive(self):
        bits = ""
        print("Waiting for a word")
        data = self.sm.get()				# wait for a bit detected from the FIFO
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
            if self.sm.rx_fifo() > 0:
                data = self.sm.get()
            else:
                data = 0
            if elapsed_time > 100:
                break
        # we've time out -- that means we're at the end of a word
        print(f"Received %d Bits: %s" % (len(bits), bits))
        if len(bits) == 4:
            value = int(bits, 2)
            print(f"Value = %s" % (hex(value)))
        elif len(bits) == 37:
            value = int(bits[:-1], 2)                # don't look at the last bit when calculating value
            print(f"Value = %s" % (hex(value)))
            a = bits[1:18].count('1')
            parity_front = a % 2
            b = bits[18:36].count('1') + 1
            parity_back = b % 2
            print(f"Parity bits should be %d and %d" % (parity_front, parity_back))
        else:
            value = int(bits[:-1], 2)                # don't look at the last bit when calculating value
            print(f"Value = %s", (hex(value)))
        return bits
       
if __name__ == "__main__":
    wt = WeigandTranslator()
    while True:
        bits = wt.Receive()
        if len(bits) == 4:       # is it a digit
            while wt.AccumulateBits(bits):
                bits = wt.Receive()
                pass
            bits = wt.GetAccumulatedBits()
            bits = wt.CalculateParity(bits)
        wt.Transmit(bits)
              
        


