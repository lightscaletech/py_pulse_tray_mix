from py_pulse_tray_mixer import lib_pulseaudio as pa
import ctypes as c

_pa_ml = None
_pa_ctx = None

def pause(): pa.pa_threaded_mainloop_lock(_pa_ml)
def resume(): pa.pa_threaded_mainloop_unlock(_pa_ml)

def _py_ctx_event(ctx, name, prop_list, ud):
    print("hello world")

_ctx_event = pa.pa_context_event_cb_t(_py_ctx_event)

def _py_ctx_state(ctx, ud):
    print(pa.pa_context_get_state(ctx))

_ctx_state = pa.pa_context_notify_cb_t(_py_ctx_state)

def start():
    _pa_ml = pa.pa_threaded_mainloop_new()
    ml_api = pa.pa_threaded_mainloop_get_api(_pa_ml)
    _pa_ctx = pa.pa_context_new(ml_api, c.c_char_p(b'Py_tray_mixer'))
    rt = pa.pa_context_connect(_pa_ctx, None, pa.PA_CONTEXT_NOFLAGS, None)

    rt = c.c_int()
    pa.pa_threaded_mainloop_start(_pa_ml)

    pa.pa_context_set_event_callback(_pa_ctx, _ctx_event, None)
    pa.pa_context_set_state_callback(_pa_ctx, _ctx_state, None)
    pa.pa_context

def stop():
    pa.pa_context_disconnect(_pa_ctx)
    pa.pa_threaded_mainloop_stop(_pa_ml)
    pa.pa_threaded_mainloop_free(_pa_ml)
