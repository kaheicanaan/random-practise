import os
from flask import Flask, request
import traceback
import requests
from datetime import datetime
from simple_counter import message_queue, query_and_cache
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--kiosk-id', default=9, type=int)
args = parser.parse_args()


KIOSK_ID = args.kiosk_id
APP_PORT = os.environ.get('APP_PORT', '24601')
APP_DEBUG_MODE = os.environ.get('APP_DEBUG_MODE', 'true')
hard_coded_candidate_name = {
    '1': 'chips',
    '2': 'lam lam',
    '3': 'justice'
}
msg_q = message_queue.MessageQueueSQS()
cache = query_and_cache.CachingLayer(expire_seconds=10)
app = Flask(__name__)


@app.route('/hello_world', methods=['GET'])
def hello_world():
    return {
        'status': 'SUCCESS',
        "payload": "Hello, World!"
    }


@app.route('/vote', methods=['POST'])
def vote():
    try:
        candidate = request.json['candidate']
        now = datetime.utcnow().strftime('%Y-%m-%d %T.%f')
        msg_q.send_vote(candidate, now, KIOSK_ID)
        return {
            'status': 'SUCCESS',
            "payload": f"Successfully voted to {hard_coded_candidate_name[candidate]} at {now}!"
        }
    except Exception as e:
        tb_msg = traceback.format_exc()
        print(tb_msg)
        return {'status': 'FAILED', 'error_messages': tb_msg}


@app.route('/voting_distribution', methods=['GET'])
def voting_distribution():
    try:
        ten_minute_last_update, ten_minute_result = cache.get_or_query_ten_minutes_result()
        total_last_update, total_result = cache.get_or_query_total_result()

        # rename candidate names
        ten_minute_result.rename(hard_coded_candidate_name, inplace=True)
        total_result.rename(hard_coded_candidate_name, inplace=True)
        return {
            'status': 'SUCCESS',
            "payload": {
                'last_10_minute': {
                    'last_update_time': ten_minute_last_update.strftime('%Y-%m-%d %T.%f'),
                    'distribution': ten_minute_result.to_dict()
                },
                'total_vote_count': {
                    'last_update_time': total_last_update.strftime('%Y-%m-%d %T.%f'),
                    'distribution': total_result.to_dict()
                },
            }
        }
    except Exception as e:
        tb_msg = traceback.format_exc()
        print(tb_msg)
        return {'status': 'FAILED', 'error_messages': tb_msg}


# =================
# for easier voting
# =================
@app.route('/vote_to_1', methods=['GET'])
def vote_to_1():
    response = requests.post('http://home.kahei.io:24601/vote', json={'candidate': '1'})
    return response.json()


@app.route('/vote_to_2', methods=['GET'])
def vote_to_2():
    response = requests.post('http://home.kahei.io:24601/vote', json={'candidate': '2'})
    return response.json()


@app.route('/vote_to_3', methods=['GET'])
def vote_to_3():
    response = requests.post('http://home.kahei.io:24601/vote', json={'candidate': '3'})
    return response.json()


if __name__ == '__main__':
    is_debug_mode = (APP_DEBUG_MODE == 'true')
    app.run(host='0.0.0.0', port=APP_PORT, debug=is_debug_mode)

