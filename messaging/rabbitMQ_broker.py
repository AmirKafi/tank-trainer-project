import pika
from pika.exceptions import AMQPChannelError


class RabbitMQBroker:
    def __init__(self, host: str = 'localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    def declare_queue(self, queue_name: str):
        self.channel.queue_declare(queue=queue_name)

    def publish_message(self, queue_name: str, message: str):
        queue_exits = self.check_if_queue_exists(queue_name)
        if not queue_exits:
            self.declare_queue(queue_name)

        self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)

    def check_if_queue_exists(self, queue_name: str)->bool:
        try:
            self.channel.queue_declare(queue=queue_name, passive=True)
            return True
        except AMQPChannelError:
            return False

    def consume_messages(self, queue_name: str, callback):
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()