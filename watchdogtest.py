import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    #def on_any_event(self, event):
        #print(event.event_type, event.src_path)

    def on_created(self, event):
        database[event.src_path] = chisquare(event.src_path)
        print(database)
        print("CREATED", event.src_path)

    def on_deleted(self, event):
        try:
            del database[event.src_path]
        except KeyError as e:
            print(e)

        print(database)
        print("on_deleted", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            database[event.src_path] = chisquare(event.src_path)
            print(database)
            print("MODIFIED", event.src_path)

    #def on_moved(self, event):
        #print("on_moved", event.src_path)

def chisquare(fname):
    
    print(fname)

    try:
        with open(fname, "r+b") as file:

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
                continue
            
            fname = os.path.join(root, name)
            print("The fname is : ", fname)
            _chiquare = chisquare(fname)
            db[fname] = _chiquare        

    return db

if __name__ == "__main__":
    #src_path = sys.argv[1]
    database = calc_chisquare()

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()
