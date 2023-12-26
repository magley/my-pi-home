from common.app import App
import threading
import requests


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


def on_DUS_add_userdata(app: App):
    """
    On each DUS reading, the new value is added to a data queue in app.userdata,
    accessible as 'DUS1', returned as a list.
    """

    def _on_DUS_add_userdata(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'DUS1':
            return
        
        if data['code'] != 0:
            return
        
        dist = data['distance_in_cm']
        
        with app.userdata_lock:
            li = app.userdata.get('DUS1', [])
            if len(li) > 10:
                li = li[len(li) - 10:]
            li.append(dist)
            app.userdata['DUS1'] = li


    return lambda cfg, data: _on_DUS_add_userdata(app, cfg, data)



def on_DPIR_movement_detect_person_from_DUS(app: App):
    """
    When DPIR detects movement, check DUS for whether the person is entering
    (walking towards DUS) or exiting (walking away from DUS).

    TODO: Is this logic correct?
    NOTE: This func assumes DPIR1 if the app starts for PI1 and DPIR2 otherwise.
    """

    def _on_DPIR_movement_detect_person_from_DUS(app: App, cfg: dict, data: dict):
        if cfg['name'] != f'DPIR{app.pi_id}':
            return
        
        if data['motion'] is True:
            last_readings = []
            with app.userdata_lock:
                last_readings = app.userdata.get(f'DUS{app.pi_id}', [])

            if len(last_readings) < 2:
                return
            
            data = {
                "entering": True
            }
            # If the person was closer in the past than in the present: leaving
            if last_readings[0] > last_readings[-1]:
                data['entering'] = False

            headers = {
                'Content-type':'application/json'
            }
            requests.post(f"{app.config['server']['url']}/people", json=data, headers=headers)


    return lambda cfg, data: _on_DPIR_movement_detect_person_from_DUS(app, cfg, data)