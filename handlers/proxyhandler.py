import requests
from apscheduler.schedulers.background import BackgroundScheduler
import threading

proxies = []


def get_proxies():
    global proxies
    resp = requests.get('https://proxy-listing.herokuapp.com/proxy', timeout=60)
    proxies = resp.json()


def scheduler_proxy():
    requests.get('https://proxy-listing.herokuapp.com/process', timeout=300)
    get_proxies()
    scheduler = BackgroundScheduler()
    scheduler.remove_all_jobs()
    scheduler.add_job(get_proxies, 'interval', hours=6)
    scheduler.start()


def run():
    t = threading.Thread(target=scheduler_proxy)
    t.start()
    print("Processing proxy...")
