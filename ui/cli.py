from common.app import App
import time
from datetime import datetime


def console_app(app: App):
    done = False
    while not done:
        try:
            done = _console_app(app)
        except EOFError:
            # Triggered in CLI after starting listen command, then doing Ctrl+C twice to exit program.
            # This happens without the event queue as well, probably something to do with daemon threads
            # being blocked/holding onto locks. Is this considered a hack, or is it an acceptable response?
            done = True


def _console_app(app: App):
    app.print_thread.set_paused()

    print("\nSelect command")
    print('-' * 30)
    print("listen\t\t(Use keyboard interrupt to return to menu)")
    print('quit')
    print("door-buzz-on")
    print("door-buzz-off")
    print("bedroom-buzz-on")
    print("bedroom-buzz-off")
    print("door-light-on")
    print("door-light-off")
    print("lcd-write")
    print('debug-gsg-shake')
    print('b4sd-time')
    print('rgb-color')
    print('-' * 30)
    print('Enter command:', end='')
    
    i = input()
    if i ==  'door-buzz-on':
        app.door_buzzer_on()
    elif i ==  'door-buzz-off':
        app.door_buzzer_off()  
    elif i ==  'bedroom-buzz-on':
        app.bedroom_buzzer_on()
    elif i ==  'bedroom-buzz-off':
        app.bedroom_buzzer_off()
    elif i ==  'door-light-on':
        app.door_light_on()
    elif i == 'door-light-off':
        app.door_light_off()
    elif i == 'lcd-write':
        s = input("Enter text:")
        app.lcd_write_text(s)
    elif i == 'debug-gsg-shake':
        app.gsg_debug_shake()
    elif i == 'b4sd-time':
        current_time = datetime.now().strftime('%H:%M:%S')
        app.b4sd_write_text(current_time)
    elif i == 'rgb-color':
        c = _input_rgb_color()
        app.rgb_color(c)
    elif i ==  'listen':
        app.print_thread.set_unpaused()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped listening...")
    elif i ==  'quit':
        return True
    else:
        print("Unknown command")

    return False


def _input_rgb_color():
    while True:
        s = input('Enter color: ')
        if len(s) != 3 or (s[0] != '0' and s[0] != '1') or (s[1] != '0' and s[1] != '1') or (s[2] != '0' and s[2] != '1'):
            print('Incorrect color. Format is (0|1)(0|1)(0|1)\nExample colors: "101", "110", "001"')
            continue
        return s
