import datetime
import math
import time
from common.app import App
import threading
import requests
import json
import websocket


###############################################################################
# HTTP Utility methods

def _post(app: App, data_json: dict, endpoint: str):
    headers = {
        'Content-type':'application/json'
    }
    requests.post(f"{app.config['server']['url']}/{endpoint}", json=data_json, headers=headers)


def _get(app: App, endpoint: str) -> dict:
    response = requests.get(f"{app.config['server']['url']}/{endpoint}")
    return json.loads(response.content.decode('utf-8'))

###############################################################################

# ALARM 1 [Buzz if alarm is on]
def websocket_if_alarm_then_turn_on_buzzer_else_turn_off_buzzer(app: App):
    """
    Usage
    -----
    Call it once on app startup. The websocket client runs in a background thread.

    Description
    ---
    Subscribe to ws://[server]/ws/alarm

    When I receive {'alarm': true}
        -> Turn on the buzzers
    When I receive {'alarm': false}
        -> Turn off the buzzers

    NOTE: The server should send a WS message ONLY when the alarm state changes,
    and NOT periodically. If it sends periodically, then the BUZZ/STOP_BUZZ
    events would fire up all the time, and each event would go in influxdb.
    """

    def ws_code_running_in_background_thread():
        def on_open(ws):
            pass

        def on_close(ws, close_status_code, close_msg):
            pass

        def on_error(ws, error):
            print(error)
                
        def on_message(ws, message):
            msg = json.loads(message)
            is_alarm = msg['alarm']
            with app.userdata_lock:
                app.userdata['alarm'] = is_alarm
            if is_alarm:
                app.door_buzzer_on()
                app.bedroom_buzzer_on()
            else:
                app.door_buzzer_off()
                with app.userdata_lock:
                    # Only disable BB if the wakeup timer isn't currently active
                    if not app.userdata.get('is_wakeup_active'):
                        app.bedroom_buzzer_off()

        ws = websocket.WebSocketApp(f"{app.config['server']['url_ws']}/alarm",
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message,
                            on_error=on_error)   
        ws.run_forever()
    
    thread = threading.Thread(target=ws_code_running_in_background_thread, daemon=True)
    thread.start()


# [9]
def start_threads_for_wakeup(app: App):
    """
    Usage
    -----
    Call it once on app startup. Will start threads for websocket and buzzing
    """
    def ws_code_running_in_background_thread():
        def on_open(ws):
            pass

        def on_close(ws, close_status_code, close_msg):
            pass

        def on_error(ws, error):
            print(error)
                
        def on_message(ws, message):
            """
            message can be either { "wakeup": wakeup } or { "is_wakeup_active": is_wakeup_active }
            """
            msg = json.loads(message)
            wakeup = msg.get('wakeup')
            if wakeup is not None:
                with app.userdata_lock:
                    app.userdata['wakeup'] = wakeup
                
            is_wakeup_active = msg.get('is_wakeup_active')
            if is_wakeup_active is not None:
                with app.userdata_lock:
                    app.userdata['is_wakeup_active'] = is_wakeup_active
                if is_wakeup_active:
                    app.bedroom_buzzer_on()    
                # Only disable BB if the alarm isn't currently active
                else:
                    with app.userdata_lock:
                        if not app.userdata.get('alarm'):
                            app.bedroom_buzzer_off()

        ws = websocket.WebSocketApp(f"{app.config['server']['url_ws']}/wakeup",
                            on_open=on_open,
                            on_close=on_close,
                            on_message=on_message,
                            on_error=on_error)   
        ws.run_forever()

    thread = threading.Thread(target=ws_code_running_in_background_thread, daemon=True)
    thread.start()

    def periodically_check_if_wakeup_is_active():
        while True:
            wakeup = ''
            with app.userdata_lock:
                wakeup = app.userdata.get('wakeup')
                if wakeup is None:
                    app.userdata['wakeup'] = ''
                    continue
            cur_time = datetime.datetime.now().strftime('%H:%M')
            if cur_time == wakeup:
                _post(app, {"is_wakeup_active": True}, "is_wakeup_active")
                # Sleep a minute (plus few seconds for paranoia) so we don't trigger the same alarm again
                time.sleep(62)
                continue
            time.sleep(2)


    thread = threading.Thread(target=periodically_check_if_wakeup_is_active, daemon=True)
    thread.start()


# [7]
def read_GDHT_to_GLCD(app: App):
    def _read_GDHT_to_GLCD(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'GDHT':
            return

        txt = f"T: {round(data['temperature'], 1)}\nH: {round(data['humidity'], 1)}"
        app.lcd_write_text(txt)
        
    return lambda cfg, data : _read_GDHT_to_GLCD(app, cfg, data)

# [1]
def on_DPIR_movement_turn_on_DL_for10s(app: App):
    def _on_DPIR_movement_turn_on_DL_for10s(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'DPIR1':
            return
        
        if data['motion'] is True:
            app.door_light_on()
            threading.Timer(10.0, app.door_light_off).start()


    return lambda cfg, data: _on_DPIR_movement_turn_on_DL_for10s(app, cfg, data)

# [2] Utility
def on_DUS_add_userdata(app: App):
    """
    On each DUS reading, the new value is added to a data queue in app.userdata,
    accessible as 'DUS1'/'DUS2', returned as a list.
    """

    def _on_DUS_add_userdata(app: App, cfg: dict, data: dict):
        dus_code = f'DUS{app.pi_id}'
        if cfg['name'] != dus_code:
            return
        
        if data['code'] != 0:
            return
        
        dist = data['distance_in_cm']
        
        with app.userdata_lock:
            li = app.userdata.get(dus_code, [])
            if len(li) > 10:
                li = li[len(li) - 10:]
            li.append(dist)
            app.userdata[dus_code] = li


    return lambda cfg, data: _on_DUS_add_userdata(app, cfg, data)

# [2]
def on_DPIR_movement_detect_person_from_DUS(app: App):
    """
    When DPIR detects movement, check DUS for whether the person is entering
    (walking towards DUS) or exiting (walking away from DUS).

    TODO: Is this logic correct? Apparently, this is a non-trivial problem.
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

            # If the person was closer in the past than in the present: leaving
            data = {
                "entering": True
            }
            if last_readings[0] > last_readings[-1]:
                data['entering'] = False
            _post(app, data, "people")

    return lambda cfg, data: _on_DPIR_movement_detect_person_from_DUS(app, cfg, data)

# [5]
def on_PIR_when_no_people_alarm(app: App):
    def _on_PIR_when_no_people_alarm(app: App, cfg: dict, data: dict):
        if cfg['name'] not in ['RPIR1', 'RPIR2', 'RPIR3', 'RPIR4']:
            return
        
        if data['motion'] is True:
            _post(app, {}, "rpir")


    return lambda cfg, data: _on_PIR_when_no_people_alarm(app, cfg, data)

# [6] Utility
def on_GSG_motion_add_userdata(app: App):
    """
    On each GSG reading, the new value is added to a data queue in app.userdata,
    accessible as 'GSG', returned as a list.
    ```
    app.userdata['GSG'] = [
        {
            'ax': 123,
            'ay': 456,
            'az': 789,
            'time': datetime.datetime
        },
        ...
    ]
    ```  
    """

    def _on_GSG_motion_add_userdata(app: App, cfg: dict, data: dict):
        gsg_code = f'GSG'
        if cfg['name'] != gsg_code:
            return
        
        payload = {
            'ax': data['accel.x'],
            'ay': data['accel.y'],
            'az': data['accel.z'],
            'time': datetime.datetime.now()
        }
        
        with app.userdata_lock:
            li = app.userdata.get(gsg_code, [])
            if len(li) > 10:
                li = li[len(li) - 10:]
            li.append(payload)
            app.userdata[gsg_code] = li


    return lambda cfg, data: _on_GSG_motion_add_userdata(app, cfg, data)

# [6]
def on_GSG_motion_check_for_alarm(app: App):
    def _on_GSG_motion_check_for_alarm(app: App, cfg: dict, data: dict):
        if cfg['name'] != 'GSG':
            return
        
        last_motions = app.userdata.get('GSG', [])
        if len(last_motions) < 5:
            return
        
        integral = 0
        for i in range(len(last_motions) - 1):
            p1 = last_motions[i]
            p2 = last_motions[i + 1]

            acc1 = math.sqrt(p1['ax']**2 + p1['ay']**2 + p1['az']**2)
            acc2 = math.sqrt(p2['ax']**2 + p2['ay']**2 + p2['az']**2)
            k = (acc2 + acc1) / 2 # m/s^2
            dt = (p2['time'] - p1['time']).total_seconds() # s

            v = k * dt # m/s
            integral += v

        expected_velocity = 10 * len(last_motions)
        if integral > expected_velocity * 2:
            _post(app, {'alarm': True}, '/alarm')

    return lambda cfg, data: _on_GSG_motion_check_for_alarm(app, cfg, data)


# [8] [9]
def periodically_write_current_time_to_B4SD_and_blink_if_wakeup_active(app: App):
    """
    Usage
    -----
    Call it once on app startup, the function will start a daemon thread.
    """
    def update_time():
        sleep_time = 1
        while True:
            remaining_sleep_time = sleep_time
            if app.userdata.get('is_wakeup_active'):
                remaining_sleep_time -= 0.5
                app.b4sd_blank()
                time.sleep(remaining_sleep_time)
            cur_time = datetime.datetime.now().strftime('%H:%M:%S')
            app.b4sd_write_text(cur_time)
            time.sleep(remaining_sleep_time)
    t = threading.Thread(target=update_time, daemon=True)
    t.start()
