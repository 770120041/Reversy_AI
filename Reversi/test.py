import multiprocessing
import Queue

TIMEOUT = 1

def big_loop(bob):
    import time
    time.sleep(4)
    return bob*2

def wrapper(queue, bob):
    result = big_loop(bob)
    queue.put(result)
    queue.close()

def run_loop_with_timeout():
    bob = 21 # Whatever sensible value you need
    queue = multiprocessing.Queue(1) # Maximum size is 1
    proc = multiprocessing.Process(target=wrapper, args=(queue, bob))
    proc.start()

    # Wait for TIMEOUT seconds
    try:
        result = queue.get(True, TIMEOUT)
    except Queue.Empty:
        # Deal with lack of data somehow
        result = None
    finally:
        proc.terminate()

    # Process data here, not in try block above, otherwise your process keeps running
    print result

if __name__ == "__main__":
    run_loop_with_timeout()