import psutil
import subprocess
import time
                                                                  def is_process_running(process_name):                                 for process in psutil.process_iter(['pid', 'name']):                  if process.info['name'] == process_name:                              return True                                               return False

def restart_script(script_name):
    try:
        subprocess.run(['pkill', '-f', script_name])
        time.sleep(1)  # Wait for the process to terminate
        subprocess.run(['python', script_name])                       except Exception as e:
        print(f"Error restarting {script_name}: {e}")             
if __name__ == "__main__":
    target_script = "spUpdater2.py"                               
    while True:
        if not is_process_running(target_script):                             print(f"{target_script} is not running. Restarting...>
            restart_script(target_script)                                 time.sleep(900)  # Adjust the interval as needed