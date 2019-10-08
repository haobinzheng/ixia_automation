import threading, time

def test(name, lock):
    print(name + " - Starting thread")
    print(name + " - Waiting to acquire lock")
    with lock:
        print(name + " - Lock acquired!")
        for i in range(10):

            print(name + " - " + str(i))
            print("")
            time.sleep(1)
    print(name + " - Lock released")

def main():
    lock = threading.Lock()

    t1 = threading.Thread(target=test, args=["#1_Thread", lock])
    t2 = threading.Thread(target=test, args=["#2_Thread", lock])

    t1.start()
    time.sleep(3)
    t2.start()

main()
