import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import multiprocessing
import socket

from collections import deque


def calc_queue_average():
    s = 0

    for item in global_queue:
        s += item

    return 1 if s > 0 else -1

def server_connection():
    
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(1)
    conn, address = server_socket.accept()

    while True:

        data = conn.recv(3).decode()

        if not data:
            break

        if data == "req":
            queue_average = calc_queue_average()
            print(global_queue)
            conn.send(str(queue_average).encode())
        else:
            conn.send("5".encode())

    conn.close()

def insert_into_queue(val):

    global_queue.append(val)
    

class MyHandler(FileSystemEventHandler):

    #def on_any_event(self, event):
        #print(event.event_type, event.src_path)
    def on_any_event(self, event):
        if event.src_path.startswith("./."):
            # Handle file system event here
            pass

    def on_created(self, event):
        if event.src_path[-11:] != "/mypipe.txt" and not event.src_path.startswith("./."):
            if not event.is_directory:
                print(f"TEST: {event.src_path}")
                #if os.stat(event.src_path).st_size == 0:
                #    print("ZERO SIZE")
                
                if os.path.exists(event.src_path):
                    print(f"TEST1: {event.is_directory}")

                    chi_sq = chisquare(event.src_path)
                    database[event.src_path] = chi_sq
                    print(chi_sq)
            
                    if chi_sq > 310.46: # Non-encrypted
                        insert_into_queue(-1)
                    else:
                        print(f"Created queue : {global_queue}")
                        insert_into_queue(1)
    
                #print(database)
                    print("CREATED", event.src_path)

    def on_deleted(self, event):
        if event.src_path[-11:] != "/mypipe.txt" and not event.src_path.startswith("./."):
            try:
                del database[event.src_path]
            except KeyError as e:
                print(e)

            #print(database)
            print("DELETED", event.src_path)

    def on_modified(self, event):
        if event.src_path[-11:] != "/mypipe.txt" and not event.src_path.startswith("./."):
            if not event.is_directory:
                time.sleep(1)
                chi_sq = chisquare(event.src_path)
                database[event.src_path] = chi_sq
                print(chi_sq)


                if chi_sq > 310.46: # Non-encrypted
                    insert_into_queue(-1)
                else:
                    print(f"Modified queue : {global_queue}")
                    insert_into_queue(1)

                #print(database)
                print("MODIFIED", event.src_path)

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
            if name == "mypipe.txt":
                print("EXXXXX")
                continue
            
            fname = os.path.join(root, name)
            print("The fname is : ", fname)
            _chiquare = chisquare(fname)
            db[fname] = _chiquare        

    return db

if __name__ == "__main__":
    #src_path = sys.argv[1]
    database = calc_chisquare()
    
    k = 20
    global_queue = deque([0] * k, maxlen=k)

    event_handler = MyHandler()
    # Exclude hidden folders using the ignore_patterns parameter
    # ignore_patterns = ["*/.*"]
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    print("Monitoring started")
    observer.start()

    p = multiprocessing.Process(target=server_connection)
    p.start()

    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()

