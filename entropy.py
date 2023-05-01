import os
#import sys
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import multiprocessing
import socket

timestamp_last_encryption = 0

def calc_queue_average(global_queue):
    s = 0

    for item in global_queue:   # wrong statement, doesn't work!!
        s += item

    print("[+] QUEUE TOTAL: ", s)
    return 1 if s > 0 else -1

def delta_access_time_last_encryption(access_time, last_enc_time):

    if last_enc_time != 0:
        if access_time - last_enc_time >= 10:
            return False    # User process
        else:
            return True     # Malicious process
    else:
        return False    # User process

def server_connection(global_queue, queue_total, timestamp_last_encryption):

    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(1)
    conn, address = server_socket.accept()

    while True:

        data = conn.recv(1024).decode()
        req, timestamp_access = data.split()
        print(f"[+] TIMESTAMP_ACCESS: {timestamp_access}")
        print(f"[+] TIMESTAMP_LAST_ENCRYPTION: {timestamp_last_encryption.value}")

        if not data:
            break

        if req == "req":
            if queue_total.value > 0 and delta_access_time_last_encryption(int(timestamp_access), timestamp_last_encryption.value):
                conn.send("1".encode())
            else:
                conn.send("-1".encode())
        else:
            conn.send("5".encode())

    conn.close()

def insert_into_queue(val):

    x = global_queue.get(block=False)
    queue_total.value -= x
    global_queue.put(val, block=False)
    queue_total.value += val
    
def debounce(interval):
    def decorator(f):
        def wrapper(*args, **kwargs):
            wrapper.last_invocation_time = time.time()
            if not hasattr(wrapper, 'timer'):
                wrapper.timer = None
            if wrapper.timer is not None:
                wrapper.timer.cancel()
            if time.time() - wrapper.last_invocation_time > interval:
                f(*args, **kwargs)
            else:
                wrapper.timer = threading.Timer(interval, f, args=args, kwargs=kwargs)
                wrapper.timer.start()
        return wrapper
    return decorator
    

class MyHandler(FileSystemEventHandler):

    def __init__(self):
        self.created_files = set()

    #def on_any_event(self, event):
        #print(event.event_type, event.src_path)
    
    def on_created(self, event):

        if event.src_path[-10:] != "mypipe.txt" and not event.src_path.startswith("./."):
                if not event.is_directory:
                    #print(f"TEST: {event.src_path}")
                    #if os.stat(event.src_path).st_size == 0:
                    #    print("ZERO SIZE")
                
                    if os.path.exists(event.src_path):
                        #print(f"TEST1: {event.is_directory}")

                        chi_sq = chisquare(event.src_path)
                        #database[event.src_path] = chi_sq
                    #print(chi_sq)
                        
                        if chi_sq != 0:
                            self.created_files.add(event.src_path)
                
                        if chi_sq > 310.46: # Non-encrypted
                            insert_into_queue(-1)
                            print(f"[+] CREATED QUEUE NE : {global_queue}")
                        else:
                            if chi_sq != 0:
                                timestamp_last_encryption.value = int(time.time())
                                insert_into_queue(1)
                                print(f"[+] CREATED QUEUE E : {global_queue}")
                            else:
                                print("[+] CHI_SQ CREATED = 0")
    
                #print(database)
                        print("[+] CREATED", event.src_path)
    
    
    #@debounce(1)
    def on_any_event(self, event):

        if event.src_path.startswith("./."):
            # Handle file system event here
            return
            
        if event.event_type == "created":
            return
        
        if event.event_type == "closed" and not event.is_directory:
            if event.src_path[-10:] != "mypipe.txt" and not event.src_path.startswith("./."):
                if not event.is_directory:
                    #time.sleep(1)
                    chi_sq = chisquare(event.src_path)
                    #database[event.src_path] = chi_sq
                    #print(chi_sq)

                    # check if the file was also created
                    if event.src_path in self.created_files:
                        # remove the file from the list of created files
                        self.created_files.remove(event.src_path)
                        return

                    if chi_sq > 310.46: # Non-encrypted
                        insert_into_queue(-1)
                        print(f"[+] MODIFIED QUEUE NE : {global_queue}")
                    else:
                        if chi_sq != 0:
                            timestamp_last_encryption.value = int(time.time())
                            insert_into_queue(1)
                            print(f"[+] MODIFIED QUEUE E : {global_queue}")
                        else:
                            print("[+] CHI_SQ MODIFIED = 0")

                    #print(database)
                    print("[+] MODIFIED", event.src_path)
                else:
                    print("[+] MODIFIED DIRECTORY", event.src_path)
            

    def on_deleted(self, event):
        if event.src_path[-10:] != "mypipe.txt" and not event.src_path.startswith("./."):
            #try:
            #    del database[event.src_path]
            #except KeyError as e:
            #    print(e)

            #print(database)
            print("[+] DELETED", event.src_path)

    #@debounce(1)
    #def on_modified(self, event):
    #    if event.src_path[-11:] != "/mypipe.txt" and not event.src_path.startswith("./."):
    #        if not event.is_directory:
                #time.sleep(1)
    #            chi_sq = chisquare(event.src_path)
    #            database[event.src_path] = chi_sq
                #print(chi_sq)


    #            if chi_sq > 310.46: # Non-encrypted
    #                insert_into_queue(-1)
    #                print(f"[+] MODIFIED QUEUE NE : {global_queue}")
    #            else:
    #            	if chi_sq != 0:
    #            		insert_into_queue(1)
    #            		print(f"[+] MODIFIED QUEUE E : {global_queue}")
    #            	else:
    #            		print("[+] CHI_SQ MODIFIED = 0")

                #print(database)
    #            print("[+] MODIFIED", event.src_path)
    #        else:
    #            print("[+] MODIFIED DIRECTORY", event.src_path)

    #def on_moved(self, event):
        #print("on_moved", event.src_path)

def chisquare(fname):
    
    #print(fname)

    try:
        with open(fname, "rb") as file:

            count = dict()
            c = 0
        
            for line in file:
                for ch in line:
                    c += 1
                    if ch in count:
                        count[ch] += 1
                    else:
                        count[ch] = 1 
    except FileNotFoundError as e:
        c = 0
        count = {}
        print(e)

    Ei = c / 256
    X = 0
    k = 0

    for num in count.values():
        k += 1
        X += (num - Ei) ** 2

    X += (256 - k) * (Ei ** 2)

    return X / Ei if Ei != 0 else 0

def calc_chisquare():
    db = dict()

    for root, dirs, files in os.walk(".", topdown=True):
        
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        
        for name in files:
            if name[-10:] == "mypipe.txt":
                #print("EXXXXX")
                continue
            
            fname = os.path.join(root, name)
            print("Processing: ", fname)
            _chiquare = chisquare(fname)
            db[fname] = _chiquare        

    return db

if __name__ == "__main__":

    pid = os.getpid()
    
    with open("pid.txt", "w") as file1:
        file1.write(str(pid))
    #print(read_content)
    
    
    
    # src_path = sys.argv[1]
    # database = calc_chisquare()
    #database = {}

    k = 20
    global_queue = multiprocessing.Queue(maxsize=20)    
    #deque([0] * k, maxlen=k)
    for i in range(20):
        global_queue.put(0)

    queue_total = multiprocessing.Value('i')
    queue_total.value = 0

    timestamp_last_encryption = multiprocessing.Value('i')
    timestamp_last_encryption.value = 0

    event_handler = MyHandler()
    # Exclude hidden folders using the ignore_patterns parameter
    # ignore_patterns = ["*/.*"]
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    print("Monitoring started.")
    observer.start()

    p = multiprocessing.Process(target=server_connection, args=(global_queue, queue_total, timestamp_last_encryption,))
    p.start()

    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()
