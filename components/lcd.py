from common.mqtt import MqttSender, build_payload
from components.lcd_util import PCF8574_GPIO, Adafruit_CharLCD


class LCD_Mqtt(MqttSender):
    def __init__(self, config: dict):
        super().__init__(config)
        self.topic = "iot/lcd"


    # Actuactor can have multiple events, so pass the event as well
    def put(self, cfg: dict, data: dict, event: str):
        if cfg['type'] != 'lcd':
            return

        buzz_payload = build_payload(cfg, data, event)
        self.do_put(buzz_payload)


# There's only one LCD in the project, so the state can be a global variable.
_mcp: PCF8574_GPIO = None
_lcd: Adafruit_CharLCD = None


def get_set_text(cfg: dict):
    if cfg['simulated']:
        return set_text_simulated
    return set_text


def setup():
    global _mcp
    global _lcd
    def _setup_mcp() -> PCF8574_GPIO:
        PCF8574_address = 0x27
        PCF8574A_address = 0x3F
        mcp: PCF8574_GPIO
        try:
            mcp = PCF8574_GPIO(PCF8574_address)
        except Exception:
            try:
                mcp = PCF8574_GPIO(PCF8574A_address)
            except Exception:
                print ('I2C Address Error !')
                exit(1)
        return mcp

    def _setup_lcd(mcp: PCF8574_GPIO) -> Adafruit_CharLCD:
        return Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
        
    _mcp = _setup_mcp()
    _lcd = _setup_lcd(_mcp)

    _mcp.output(3, 1)     # TODO: Is this the SCL pin?
    _lcd.begin(16, 2)


def set_text(text: str):
    _lcd.setCursor(0, 0)
    _lcd.message(text)


def set_text_simulated(text: str):
    pass