from py_pulse_tray_mixer import lib_pulseaudio as pa
import ctypes as c

class PObj(object):
    def __init__(self, info):
        self.name = info.name.decode('utf-8')
        self.index = info.index
        self.cvolume = info.volume
        self.volume = pa.pa_cvolume_max(self.cvolume)
        self.proplist = info.proplist
        self.print_proplist()

    def get_from_proplist(self, key):
        pa.pa_proplist_gets(self.proplist, key).decode('utf-8')

    def print_proplist(self):
        state = c.c_void_p(None)

        print("------------------------------------------------")
        while True:
            k = pa.pa_proplist_iterate(self.proplist, c.pointer(state))
            if k is None: break;
            print("%s: %s" %
                  (k.decode('utf-8'),
                   pa.pa_proplist_gets(self.proplist, k).decode('utf-8')))
        print("------------------------------------------------")

class Sink(PObj):
    def __init__(self, info):
        PObj.__init__(self, info)
        self.icon = self.get_from_proplist(pa.PA_PROP_DEVICE_ICON_NAME)

class Input(PObj):
    def __init__(self, info):
        PObj.__init__(self, info)
        self.name = self.get_from_proplist(pa.PA_PROP_APPLICATION_NAME)
        self.icon = self.get_from_proplist(pa.PA_PROP_APPLICATION_ICON_NAME)

class Manager(object):
    _items = {}

    change = None
    new = None
    old = None

    def __init__(self):
        pass

    def add_item(self, item):
        self._items[item.index] = item
        print ("Item added: " + str(item.index) + ', ' + item.name)

        if self.new is not None: self.new(item)

    def changed_item(self, item):
        self._items[item.index] = item

        if self.change is not None: self.change(item)

    def upsert_item(self, item):
        if item.index in self._items: self.changed_item(item)
        else: self.add_item(item)

    def remove_item(self, index):
        print ("Item removed: %i" % index)
        del self._items[index]

        if self.old is not None: self.old(index)


_sink_manager = Manager()
_input_manager = Manager()

_pa_ml = None
_pa_ctx = None

def _info_manage(t, manager, i):
    info = None
    try:
        info = i.contents
    except: pass
    if info is None: return

    manager.upsert_item(t(info))

def _sink_info(ctx, sink_info, eol, ud):
    _info_manage(Sink, _sink_manager, sink_info)

def _input_info(ctx, input_info, eol, ud):
    _info_manage(Sink, _input_manager, input_info)

def _ctx_sub_success(ctx, success, ud): pass

def _ctx_sub_cb(ctx, evt, eid, ud):
    evtype = evt & pa.PA_SUBSCRIPTION_EVENT_TYPE_MASK
    evfac = evt & pa.PA_SUBSCRIPTION_EVENT_FACILITY_MASK

    if(evfac == pa.PA_SUBSCRIPTION_EVENT_SINK):
        if evtype == pa.PA_SUBSCRIPTION_EVENT_REMOVE:
            _sink_manager.remove_item(eid)
        else: _request_sink_state(ctx, eid, evtype)
    if(evfac == pa.PA_SUBSCRIPTION_EVENT_SINK_INPUT):
        if evtype == pa.PA_SUBSCRIPTION_EVENT_REMOVE:
            _input_manager.remove_item(eid)
        else: _request_input_state(ctx, eid, evtype)

def _ctx_event(ctx, name, prop_list, ud): print("Context event")

def _ctx_state(ctx, ud):
    state = pa.pa_context_get_state(ctx)

    if state == pa.PA_CONTEXT_READY:
        _request_sinks(ctx, pa.PA_SUBSCRIPTION_EVENT_NEW)
        _request_inputs(ctx, pa.PA_SUBSCRIPTION_EVENT_NEW)
        pa.pa_context_set_subscribe_callback(ctx, _c_ctx_sub_cb ,None)
        pa.pa_context_subscribe(ctx,
                                pa.PA_SUBSCRIPTION_MASK_SINK |
                                pa.PA_SUBSCRIPTION_MASK_SINK_INPUT,
                                _c_ctx_sub_success, None)
        print ("Ready!")

_c_ctx_sub_success = pa.pa_context_success_cb_t( _ctx_sub_success )
_c_ctx_sub_cb      = pa.pa_context_subscribe_cb_t( _ctx_sub_cb )
_c_ctx_state       = pa.pa_context_notify_cb_t( _ctx_state )
_c_ctx_event       = pa.pa_context_event_cb_t( _ctx_event )
_c_sink_info       = pa.pa_sink_info_cb_t( _sink_info )
_c_input_info      = pa.pa_sink_input_info_cb_t( _input_info )


def _request_sinks(ctx, event=None):
    pa.pa_context_get_sink_info_list(ctx, _c_sink_info, event)

def _request_sink_state(ctx, id, event=None):
    pa.pa_context_get_sink_info_by_index(ctx, id, _c_sink_info, event)

def _request_inputs(ctx, event=None):
    pa.pa_context_get_sink_input_info_list(ctx, _c_input_info, event)

def _request_input_state(ctx, id, event=None):
    pa.pa_context_get_sink_input_info(ctx, id, _c_input_info, event)


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
