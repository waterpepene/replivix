import requests as r
import threading
import random
url = r"http://www.drbike.co.th/backend/js/lang/zz/ment.php"

def spam():
    for i in range(100):
        data = {"username": "loser" + str(random.randint(0, 10000)), "password": "loser_stop_it" + str(i), "mobile": "0"}
        request = r.post(url, data=data)
        print(request.status_code)


# start 10 threads to spam
for i in range(10):
    threading.Thread(target=spam).start()
