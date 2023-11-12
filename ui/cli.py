from common.app import App
import time


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
    print("room-buzz-on")
    print("room-buzz-off")
    print("door-light-on")
    print("door-light-off")
    print('-' * 30)
    print('Enter command:', end='')

    match input():
        case 'room-buzz-on':
            app.room_buzzer_on()
        case 'room-buzz-off':
            app.room_buzzer_off()
        case 'door-light-on':
            app.door_light_on()
        case 'door-light-off':
            app.door_light_off()
        case 'listen':
            app.print_thread.set_unpaused()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Stopped listening...")
        case 'quit':
            return True
        case _:
            print("Unknown command")

    return False
