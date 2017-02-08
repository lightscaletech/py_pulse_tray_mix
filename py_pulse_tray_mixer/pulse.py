from py_pulse_tray_mixer import lib_pulseaudio as pa
import ctypes as c

class PObj(Object):
    def __init__(self, info):
        self.name = info.name.value.decode('utf-8')
        self.index = info.index.value
        self.volume = info.volume
        self.proplist = info.proplist

class Sink(PObj):
    def __init__(self, info):
        PObj.__init__(self, info)

class Source(PObj):
    def __init__(self, info):
        PObj.__init__(self, info)

class Manager(Object):
    _items = {}

    change = None
    new = None
    old = None

    def __init__(self):
        pass

    def add_item(self, item):
        self._items[item.index] = item
        if new is not None: new(item)

    def remove_item(self, item):
        del self._items[item.index]
        if old is not None: old(item)

    def changed_item(self, item):
        if item.index in self._items: return self.add_item(item)
        else: self._items[item.index] = item
        if change is not None: change(item)

_pa_ml = None
_pa_ctx = None

def _sink_info_list(ctx, sink_info, eol, ud):
    print("sink info list")
    print(sink_info)

def _sink_info(ctx, sink_info, eol, ud):
    print("Sink info")

def _request_sinks(ctx):
    pa.pa_context_get_sink_info_list(ctx, _c_sink_info_list, None)

def _request_sink_state(ctx, id, event=None):
    pa.pa_context_get_sink_info_by_index(ctx, id, _c_sink_info)

def _ctx_sub_cb(ctx, evt, eid, ud):
    print(evt)
    pass

def _ctx_event(ctx, name, prop_list, ud):
    print("Context event")

def _ctx_state(ctx, ud):
    state = pa.pa_context_get_state(ctx)
    if state == pa.PA_CONTEXT_READY:
        print ("Ready!")
        _request_sinks(ctx)
        pa.pa_context_set_subscribe_callback(ctx, _c_ctx_sub_cb ,None)
        pa.pa_context_subscribe(ctx,
                                pa.PA_SUBSCRIPTION_MASK_ALL,
                                None, None)

_c_ctx_sub_cb     = pa.pa_context_subscribe_cb_t( _ctx_sub_cb )
_c_ctx_state      = pa.pa_context_notify_cb_t( _ctx_state )
_c_ctx_event      = pa.pa_context_event_cb_t( _ctx_event )
_c_sink_info_list = pa.pa_sink_info_cb_t( _sink_info_list )
_c_sink_info      = pa.pa_sink_info_cb_t( _sink_info )

def pause(): pa.pa_threaded_mainloop_lock(_pa_ml)
def resume(): pa.pa_threaded_mainloop_unlock(_pa_ml)

def start():
    _pa_ml = pa.pa_threaded_mainloop_new()
    ml_api = pa.pa_threaded_mainloop_get_api(_pa_ml)
    _pa_ctx = pa.pa_context_new(ml_api, c.c_char_p(b'Py_tray_mixer'))
    rt = pa.pa_context_connect(_pa_ctx, None, pa.PA_CONTEXT_NOFLAGS, None)

    rt = c.c_int()
    pa.pa_threaded_mainloop_start(_pa_ml)

    pa.pa_context_set_event_callback(_pa_ctx, _c_ctx_event, None)
    pa.pa_context_set_state_callback(_pa_ctx, _c_ctx_state, None)


def stop():
    pa.pa_context_disconnect(_pa_ctx)
    pa.pa_threaded_mainloop_stop(_pa_ml)
    pa.pa_threaded_mainloop_free(_pa_ml)
