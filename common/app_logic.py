from common.app import App


def read_GDHT_to_GLCD(app: App):
    return lambda cfg, data : _read_GDHT_to_GLCD(app, cfg, data)


def _read_GDHT_to_GLCD(app: App, cfg: dict, data: dict):
    '''
        `app` Provided by the public API during partial function application.
        `cfg` Filter all funcs except GDHT.
        `data` Read by GDHT.
    '''

    if cfg['name'] != 'GDHT':
        return
    
    txt = f"T: {data['temperature']}\nH: {data['humidity']}"
    app.lcd_write_text(txt)