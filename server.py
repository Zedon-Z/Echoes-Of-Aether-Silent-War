from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

executors = {
    'default': ThreadPoolExecutor(10)
}

scheduler = BackgroundScheduler(executors=executors)
scheduler.start()
app = Flask(__name__)

@app.route('/')
def home():
    return 'Echoes of Aether Telegram Bot is Live'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8443))
    app.run(host='0.0.0.0', port=port)
