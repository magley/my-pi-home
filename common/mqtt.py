import json
import paho.mqtt.publish as publish
import threading


class MqttSender:
    def __init__(self, config: dict):
        self.batch = []
        self.limit = 5
        self.config = config
        self.counter_lock = threading.Lock()
        self.pub_event = threading.Event()
        self.topic = None

        self.pub_thread = threading.Thread(target=self.pub_task)
        self.pub_thread.daemon = True
        self.pub_thread.start()


    def put(self, cfg: dict, data: dict):
        """
        `put` transforms `data` into a payload dict and publishes the data using
        `do_put`. Each mqtt class must override this method. 
        """
        raise Exception("Abstract method. Did you forget to implement it when creating a new class?")


    def on_flush(self):
        self.pub_event.set()
    

    def do_put(self, payload: dict):
        """
        API funciton called when a new item is to be sent to MQTT.

        `payload` - Device signal data converted into a proper payload, e.g.:
        ```
        {
            "mesasurement":"temperature",
            "simulated": True,
            "run_on": "PI1",
            "name": "RDHT1",
            "value": 39.0
        }
        ```

        `cfg` - Device configuration.
        """
        
        if self.topic is None:
            raise Exception("MQTT Topic must not be None. Did you forget to set it when creating a new class?")

        mqtt_msg = (self.topic, json.dumps(payload), 0, True) # Topic, payload, QOS, Retained
        with self.counter_lock:
            self.batch.append(mqtt_msg)

        if len(self.batch) >= self.limit:
            self.on_flush()


    def pub_task(self):
        """
        Wait for `pub_event`, take all data from `batch` and publish it to MQTT.

        This funtion must run in a background thread.
        """
        
        while True:
            self.pub_event.wait()

            local_batch = []
            with self.counter_lock:
                local_batch = self.batch.copy()
                self.batch.clear()

            publish.multiple(
                local_batch, 
                hostname=self.config['mqtt']['host'],
                port=self.config['mqtt']['port']
            )

            self.pub_event.clear()


def build_payload(cfg: dict, data: dict, field: str):
    """
    Given the device config, the last reading and the name of the field of interest,
    create a dictionary suitable for sending to MQTT (and storing in influxdb):
    ```
    {
        "measurement": field,
        "simulated": cfg["simulated"],
        "runs_on": cfg["runs_on"],
        "name": cfg["name"],
        "value": data[field] 
    } 
    ```
    """
    
    return {
        "measurement": field,
        "simulated": cfg["simulated"],
        "runs_on": cfg["runs_on"],
        "name": cfg["name"],
        "value": data[field]
    }