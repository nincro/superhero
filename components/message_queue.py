import redis

# Using Redis to make the message queue
# !!Caution!! This one is just to simplify the implementation,
# if we need to support multiple client,
# a professional MessageQueue component like Kafka would be a better choice.
# Different client can subscribe the update from the topic in the kafka
class MessageQueue:
    def __init__(self, redis_host="localhost", redis_port=6379, queue_name="superhero_queue"):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        self.queue_name = queue_name

    def produce(self, message):
        # Push a message to the Redis queue
        self.redis.rpush(self.queue_name, message)

    def consume(self):
        # Block until a message is available, then pop it from the Redis queue
        _, message = self.redis.blpop(self.queue_name)
        return message
