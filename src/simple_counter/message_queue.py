import os
import json
import boto3
from typing import List, Tuple


class MessageQueueSQS:
    def __init__(self):
        self._session = boto3.Session()
        self._sqs = self._session.client('sqs')
        self._queue_url = os.environ.get('SQS_URL', 'https://sqs.ap-southeast-1.amazonaws.com/660522005331/test-queue')

    def send_vote(self, candidate: str, now: str, kiosk_id: int) -> bool:
        """
        Return a bool indicating whether the message has published to SQS
        :param candidate:
        :param now:
        :param kiosk_id:
        :return:
        """
        msg = json.dumps({
            'candidate': candidate,
            'vote_time': now,
            'kiosk_id': kiosk_id
        })
        send_response = self._sqs.send_message(
            QueueUrl=self._queue_url,
            MessageBody=msg
        )
        return send_response['ResponseMetadata']['HTTPStatusCode'] == 200

    def receive_votes(self) -> Tuple[List[dict], List[dict]]:
        """
        Return both list of candidate and msg receive-handle for msg deletion later
        :return:
        """
        received_response = self._sqs.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,  # assume the request can be handled in 10 seconds
            WaitTimeSeconds=2
        )
        if received_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            if 'Messages' in received_response:
                # candidates
                bodies = [msg['Body'] for msg in received_response['Messages']]
                votes = [json.loads(body) for body in bodies]
                # message id
                msg_ids = [msg['MessageId'] for msg in received_response['Messages']]
                # receive handle
                handles = [msg['ReceiptHandle'] for msg in received_response['Messages']]
                return votes, [{'Id': _id, 'ReceiptHandle': handle} for _id, handle in zip(msg_ids, handles)]
            else:
                return [], []
        else:
            return [], []

    def delete_handled_msg(self, handles: List[dict]) -> bool:
        """
        Return a bool indicating whether deleting messages successfully
        :param handles:
        :return:
        """

        response = self._sqs.delete_message_batch(
            QueueUrl=self._queue_url,
            Entries=handles
        )
        # assume all msg is deleted successfully
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            if 'Successful' in response:
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    # for testing
    msg_q = MessageQueueSQS()
    print(msg_q.send_vote('2'))
    votes, msg_handles = msg_q.receive_votes()
    print(votes)
    print(msg_q.delete_handled_msg(msg_handles))
