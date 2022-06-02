#!/usr/bin/env python

import pika
import os

rabbitmq_server = os.environ.get('RABBITMQ_SERVER', 'localhost')
rabbitmq_user = os.environ.get('RABBITMQ_USER', 'rabbitmq')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD', 'rabbitmq')

# credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
parameters = pika.ConnectionParameters(rabbitmq_server, 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue='jobs', durable=True)
channel.queue_bind(queue='jobs', exchange='scrape')

def callback(ch, method, properties, body):
    print(" [x] Recieved %r" % body.decode())
    
    ch.basic_ack(delivery_tag = method.delivery_tag)

def consume():
    channel.basic_consume(queue="jobs", auto_ack=False, on_message_callback=callback)
    print(' [*] Waiting for messages.')
    channel.start_consuming()

consume()