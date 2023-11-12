
from common.app import App


def gui_app(app: App):
    app.print_thread.set_unpaused()
    import guizero as gz
    gui = gz.App(title="my pi home gui")
    gz.PushButton(gui, text="Toggle buzzer on", command=app.room_buzzer_on)
    gz.PushButton(gui, text="Toggle buzzer off", command=app.room_buzzer_off)
    gz.PushButton(gui, text="Door light on", command=app.door_light_on)
    gz.PushButton(gui, text="Door light off", command=app.door_light_off)
    gui.display()
