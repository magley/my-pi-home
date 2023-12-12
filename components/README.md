# On creating a new type of device

## Sensor

- All of the code goes in a single `.py` module.
- The sensor should have a `setup` function, used to initialize RPi pins.
- The sensor should have 2 reading functions: `read_sim` and `read_real`.
- Both reading functions return a `dict` with the same schema.
- `read_sim` should not be in an infinite loop or in a background thread.
- The sensor should have a `get_reader_func`.
- `get_reader_func` must take a `device_config` (a `dict`).
- `get_reader_func` must return a parameterless version of `read_sim`/`read_real` depending on the `simulated` field.
- `setup` and `get_reader_func` are the only public functions for the module.
- To make the device eligible for `setup`-ing, add another `elif` clause in `common.app.App::setup_devices`.
- To make the device eligible for reading, add another `elif` clause in `common.app.App::start_device_runners`.

## Actuator

- All of the code goes in a single `.py` module.
- For each event the device can react to, there should be two event functions.
- One event function is for the `simulated` case, other is for the `real` case.
- Simulated event functions should not do anything.
- For each event the device can react to, there should also be a `get_*` function.
- The "get event function" must return a parameterless version of the corresponding "event function" depending on the `simulated` field.
- To make the device eligible for accepting events, add another `elif` clause in `common.app.App::start_event_thread`.