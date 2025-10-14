# File to configure kafka
import os

kafka_config = {
    "bootstrap_servers": f"{os.getenv('KAFKA_HOST')}:{os.getenv('KAFKA_PORT')}",
    "security_protocol": "PLAINTEXT",
}