from py_pulse_tray_mixer import lib_pulseaudio as pa
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import ctypes as c


class PObj(object):
    def __init__(self, info):
        self.name = info.name.decode('utf-8')
        self.index = info.index
        self.cvolume = info.volume
        self.volume = pa.pa_cvolume_avg(self.cvolume)
        self.proplist = info.proplist

    def get_from_proplist(self, key):
        key = c.c_char_p(key.encode('utf-8'))
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

class PulseMainloop(QObject):

    class Worker(QObject):
        def __init__(self, ml):
            self.ml

        def loop(self):
            pa.pa_mainloop_iterate(self.ml)
            pass

    def __init__(self):
        self.ml = pa.pa_mainloop_new()

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.finished.connect(self.worker.deleteLater())

class Pulse(QOject):
    sink_manager = Manager()
    input_manager = Manager()

    _pa_ml = None
    _pa_ctx = None

    _c_ctx_sub_success = pa.pa_context_success_cb_t( self._ctx_sub_success )
    _c_ctx_sub_cb      = pa.pa_context_subscribe_cb_t( self._ctx_sub_cb )
    _c_ctx_state       = pa.pa_context_notify_cb_t( self._ctx_state )
    _c_ctx_event       = pa.pa_context_event_cb_t( self._ctx_event )
    _c_sink_info       = pa.pa_sink_info_cb_t( self._sink_info )
    _c_input_info      = pa.pa_sink_input_info_cb_t( self._input_info )

    @staticmethod
    def _upsert_manage(t, manager, i):
        info = None
        try:
            info = i.contents
        except: pass
        if info is None: return

        manager.upsert_item(t(info))

    def __init__(self, ml):
        self._pa_ml = ml

    def _sink_info(self, ctx, sink_info, eol, ud):
        self._upsert_manage(Sink, sink_manager, sink_info)

    def _input_info(self, ctx, input_info, eol, ud):
        self._upsert_manage(Sink, input_manager, input_info)

    def _ctx_sub_success(self, ctx, success, ud): pass

    def _ctx_sub_cb(self, ctx, evt, eid, ud):
        evtype = evt & pa.PA_SUBSCRIPTION_EVENT_TYPE_MASK
        evfac = evt & pa.PA_SUBSCRIPTION_EVENT_FACILITY_MASK

        if(evfac == pa.PA_SUBSCRIPTION_EVENT_SINK):
            if evtype == pa.PA_SUBSCRIPTION_EVENT_REMOVE:
                self.sink_manager.remove_item(eid)
            else: self._request_sink_state(ctx, eid, evtype)
        if(evfac == pa.PA_SUBSCRIPTION_EVENT_SINK_INPUT):
            if evtype == pa.PA_SUBSCRIPTION_EVENT_REMOVE:
                self.input_manager.remove_item(eid)
            else: self._request_input_state(ctx, eid, evtype)

    def _ctx_event(self, ctx, name, prop_list, ud): print("Context event")

    def _ctx_state(self, ctx, ud):
        state = pa.pa_context_get_state(ctx)

        if state == pa.PA_CONTEXT_READY:
            self._request_sinks(ctx, pa.PA_SUBSCRIPTION_EVENT_NEW)
            self._request_inputs(ctx, pa.PA_SUBSCRIPTION_EVENT_NEW)
            pa.pa_context_set_subscribe_callback(ctx, self._c_ctx_sub_cb ,None)
            pa.pa_context_subscribe(ctx,
                                    pa.PA_SUBSCRIPTION_MASK_SINK |
                                    pa.PA_SUBSCRIPTION_MASK_SINK_INPUT,
                                    _c_ctx_sub_success, None)
            print ("Ready!")

    def _request_sinks(self, ctx, event=None):
        pa.pa_context_get_sink_info_list(ctx, self._c_sink_info, event)

    def _request_sink_state(self, ctx, id, event=None):
        pa.pa_context_get_sink_info_by_index(ctx, id, self._c_sink_info, event)

    def _request_inputs(self, ctx, event=None):
        pa.pa_context_get_sink_input_info_list(ctx, self._c_input_info, event)

    def _request_input_state(self, ctx, id, event=None):
        pa.pa_context_get_sink_input_info(ctx, id, self._c_input_info, event)

    def start(self):
        self._pa_ml = pa.pa_threaded_mainloop_new()

        ml_api = pa.pa_threaded_mainloop_get_api(self_pa_ml)
        self._pa_ctx = pa.pa_context_new(ml_api, c.c_char_p(b'Py_tray_mixer'))

        rt = pa.pa_context_connect(self._pa_ctx, None, pa.PA_CONTEXT_NOFLAGS, None)

        rt = c.c_int()
        pa.pa_threaded_mainloop_start(self._pa_ml)

        pa.pa_context_set_event_callback(self._pa_ctx, self._c_ctx_event, None)
        pa.pa_context_set_state_callback(self._pa_ctx, self._c_ctx_state, None)


    def stop(self):
        pa.pa_context_disconnect(self._pa_ctx)
        pa.pa_threaded_mainloop_stop(self._pa_ml)
        pa.pa_threaded_mainloop_free(self._pa_ml)
