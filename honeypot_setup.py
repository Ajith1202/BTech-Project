import os
import subprocess
import signal
import sys

if __name__ == "__main__":

    path = "./mypipe"
    mode = 0o600

    try:
        if not os.path.exists(os.getcwd() + "/mypipe"):
            os.mkfifo(path, mode)

        pwd = os.getcwd()
        count = 1

        for dirpath, dirname, filename in os.walk(pwd):
            dirname[:] = [d for d in dirname if not (d[0] == '.' or d == pwd)]
            #print(dirpath)
            if count > 1:
                command_str = f'ln -sf "{pwd + "/mypipe"}" "{dirpath + "/mypipe"}"'.format(pwd + "/mypipe", dirpath + "/mypipe")
                #print(command_str)
                command = subprocess.run([command_str], shell=True, capture_output=True)
                #print(command.returncode)

            count += 1
    
    except OSError as e:
        print ("Failed to create FIFO: %s" % e)
        sys.exit()
    else:
        while True:

            with open(path, "w") as fifo:
                fifo.write("hello")

            #fifo = open(path, 'w')
            #fifo.write("hello")
            
            #command = subprocess.run(["echo", '"hello"', ">>", "./mypipe"])
            #command = subprocess.run(["sudo ausearch -f mypipe --interpret | tail -4  | grep -oh \"comm=\w*-*\w*\" "], shell=True, capture_output=True)
            #command = subprocess.run(["sudo ausearch -f mypipe --interpret | tail -4  | grep -oh \"[[:blank:]]pid=\w*\" "], shell=True, capture_output=True)
            command = subprocess.run(["sudo ausearch -f mypipe -sc openat -sv yes --interpret | tail -4 | grep \"SYSCALL\" | grep -oh \"[[:blank:]]pid=\w*\" "], shell=True, capture_output=True)
            pid_process = int(command.stdout.decode().split("=")[1].strip("\n"))
            print(f"The PID of the process accessing the file is: {pid_process}") 
            
            kill_process = input("Do you want to kill the process(y/n)?")

            if (kill_process == "y"):
                try:
                    os.kill(pid_process, signal.SIGKILL)
                except ProcessLookupError as e:
                    print ("Failed to kill process: %s" % e)
            else:
                fifo.close()
            
            # delete mypipe
            os.remove(path)
            # create new named pipe with same name so that symlinks are preserved
            os.mkfifo(path, mode)
    
