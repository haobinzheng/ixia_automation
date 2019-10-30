import argparse
from threading import Thread
import threading
import time

tLock = threading.Lock()


class AsyncWrite(threading.Thread):
    def __init__(self, text, out):
        threading.Thread.__init__(self)
        self.text = text
        self.out = out

    def run(self):
        f = open(self.out, "a")
        f.write(self.text + '\n')
        f.close()
        time.sleep(2)
        print("Finished Background File Write to " + self.out)


def Main_async():
    message = input("Enter a string to store:")
    background = AsyncWrite(message, 'tmp/out.txt')
    background.start()
    print("The program can continue while it writes in another thread")
    print("100 + 400 = ", 100 + 400)
    background.join()
    print("Waited until thread was complete")


def timer(name, delay, repeat):
    print("Timer: " + name + "Started")
    tLock.acquire()
    print(name + " has acquired the lock")
    while repeat > 0:
        time.sleep(delay)
        print(name + ": " + str(time.ctime(time.time())))
        repeat -= 1
    print(name + " is releasing the lock")
    tLock.release()
    print("Timer: " + name + " Completed")


def fib(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a


def Main_thread():
    t1 = Thread(target=timer, args=("Timer1", 1, 5))
    t2 = Thread(target=timer, args=("Timer2", 2, 5))
    t1.start()
    t2.start()

    print("Main Completed")


def Main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("num", help="The fibnacci number you wish to calcualte.", type=int)
    parser.add_argument("-o", "--output", help="Ouput result to a file.", action="store_true")

    args = parser.parse_args()

    result = fib(args.num)
    if args.verbose:
        print("The " + str(args.num) + "the fib number is " + str(result))
    elif args.quiet:
        print(result)
    else:
        print("Fib({})={}".format(args.num, result))


if __name__ == "__main__":
    Main_thread()
    # Main_async()
