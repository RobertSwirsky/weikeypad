from machine import Timer

global x

if __name__ == "__main__":
    x = 0
    tim = Timer(period=10, mode=Timer.PERIODIC, callback=lambda t:globals().__setitem__('x', x + 1))
    while True:
        print(x)
        