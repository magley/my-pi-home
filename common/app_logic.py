from common.app import App
import threading


def read_GDHT_to_GLCD(app: App):
    def _read_GDHT_to_GLCD(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'GDHT':
            return
        
        txt = f"T: {data['temperature']}\nH: {data['humidity']}"
        app.lcd_write_text(txt)
        
    return lambda cfg, data : _read_GDHT_to_GLCD(app, cfg, data)


def on_DPIR_movement_turn_on_DL_for10s(app: App):
    def _on_DPIR_movement_turn_on_DL_for10s(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'DPIR1':
            return
        
        if data['motion'] is True:
            app.door_light_on()
            threading.Timer(10.0, app.door_light_off).start()


    return lambda cfg, data: _on_DPIR_movement_turn_on_DL_for10s(app, cfg, data)




