from py_pulse_tray_mixer import lib_pulseaudio as pa
import ctypes as c

_pa_ml = None
_pa_ctx = None

def pause(): pa.pa_threaded_mainloop_lock(_pa_ml)
def resume(): pa.pa_threaded_mainloop_unlock(_pa_ml)

def start():
    _pa_ml = pa.pa_threaded_mainloop_new()
    ml_api = pa.pa_threaded_mainloop_get_api(_pa_ml)
    _pa_ctx = pa.pa_context_new(ml_api, c.c_char_p(b'Py_tray_mixer'))
    rt = pa.pa_context_connect(_pa_ctx, None, pa.PA_CONTEXT_NOFLAGS, None)

    rt = c.c_int()
    pa.pa_threaded_mainloop_start(_pa_ml)

def stop():
    pa.pa_context_disconnect(_pa_ctx)
    pa.pa_threaded_mainloop_stop(_pa_ml)
    pa.pa_threaded_mainloop_free(_pa_ml)
