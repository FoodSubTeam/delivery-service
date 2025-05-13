from confluent_kafka import Producer, Consumer, KafkaError
from kafka.admin import KafkaAdminClient, NewTopic

kafka_bootstrap_servers = 'kafka-service.kafka.svc.cluster.local:9092'

class KafkaProducerSingleton:
    _producer = None

    @classmethod
    def get_producer(cls):
        if cls._producer is None:
            cls._producer = Producer({
                'bootstrap.servers': kafka_bootstrap_servers,
                'client.id': 'kitchen-service-producer'
            })
        return cls._producer

    @classmethod
    def produce_message(cls, topic, message):
        producer = cls.get_producer()
        producer.produce(topic, message)
        producer.flush()

class KafkaConsumerSingleton:
    _consumer = None

    @classmethod
    def get_consumer(cls):
        if cls._consumer is None:
            cls._consumer = Consumer({
                'bootstrap.servers': kafka_bootstrap_servers,
                'group.id': 'kitchen-consumer-group',
                'auto.offset.reset': 'earliest'  # or 'latest'
            })
        return cls._consumer

    @classmethod
    def consume_message(cls, topics):
        consumer = cls.get_consumer()
        consumer.subscribe(topics)
        try:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                return None
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print(f"End of partition reached {msg.partition}, offset {msg.offset}")
                else:
                    print(f"Error: {msg.error()}")
            else:
                return msg.value().decode('utf-8')
        except Exception as e:
            print(f"Error consuming message: {e}")
            return None

    @classmethod
    def close(cls):
        if cls._consumer:
            cls._consumer.close()


def setup_topic(topic_name: str):
    admin_client = KafkaAdminClient(
        bootstrap_servers=kafka_bootstrap_servers,
        client_id="init-check"
    )
    topics = admin_client.list_topics()
    if topic_name not in topics:
        admin_client.create_topics([NewTopic(topic_name, num_partitions=1, replication_factor=1)])


def init_topics():
    required_topics = ["kitchen.order"]
    for topic in required_topics:
        setup_topic(topic)