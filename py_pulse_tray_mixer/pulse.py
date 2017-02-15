from py_pulse_tray_mixer import lib_pulseaudio as pa
from PyQt5.QtCore import QThread, QMutex, QObject, pyqtSignal, pyqtSlot
import ctypes as c

VOLUME_MIN = pa.PA_VOLUME_MUTED.value
VOLUME_NORM = pa.PA_VOLUME_NORM.value

class PObj(QObject):
    def __init__(self, info):
        QObject.__init__(self, None)
        self.name = info.name.decode('utf-8')
        self.title = ""
        self.index = info.index
        self.cvolume = info.volume
        self.volume = pa.pa_cvolume_avg(self.cvolume)
        self.proplist = info.proplist
        self.mute = bool(info.mute)

    def get_from_proplist(self, key):
        key = c.c_char_p(key.encode('latin-1'))
        res = pa.pa_proplist_gets(self.proplist, key)
        if type(res) is bytes: return res.decode('utf-8')

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
        self.title = self.get_from_proplist(u'alsa.card_name')
        if not self.title:
            self.title = info.name.decode('utf-8')

class Input(PObj):
    def __init__(self, info):
        PObj.__init__(self, info)
        self.title = self.get_from_proplist(pa.PA_PROP_APPLICATION_NAME)
        self.icon = self.get_from_proplist(pa.PA_PROP_APPLICATION_ICON_NAME)

class Manager(QObject):
    _items = {}

    added   = pyqtSignal(PObj)
    changed = pyqtSignal(PObj)
    removed = pyqtSignal(int)

    def add_item(self, item):
        self._items[item.index] = item
        print ("Item added: " + str(item.index) + ', ' + item.name)
        self.added.emit(item)

    def changed_item(self, item):
        self._items[item.index] = item
        self.changed.emit(item)

    def upsert_item(self, item):
        if item.index in self._items: self.changed_item(item)
        else: self.add_item(item)

    def remove_item(self, index):
        print ("Item removed: %i" % index)
        if index not in self._items: return
        del self._items[index]
        self.removed.emit(index)

class PulseMainloop(QObject):

    class Worker(QObject):
        def __init__(self, ml):
            QObject.__init__(self, None)
            self.ml = ml
            self.runLock = QMutex()
            self.run = False

        def __del__(self):
            del self.run

        def set_run(self, val):
            self.runLock.lock()
            self.run = val
            self.runLock.unlock()

        def get_run(self):
            self.runLock.lock()
            val = self.run
            self.runLock.unlock()
            return val

        def stop(self):
            print("Worker stopping")
            self.set_run(False)
            pa.pa_mainloop_wakeup(self.ml)

        @pyqtSlot()
        def start(self):
            print("started")
            self.set_run(True)
            ret = c.c_int(0)
            while self.get_run():
                pa.pa_mainloop_iterate(self.ml, 1, c.pointer(ret))
            print("stopped")

    go = pyqtSignal()
    worker = None

    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.ml = pa.pa_mainloop_new()
        self.thread = None

    def __del__(self):
        pa.pa_mainloop_free(self.ml)

    def get_api(self):
        return pa.pa_mainloop_get_api(self.ml)

    def stop(self):
        if self.worker is not None:
            self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        del self.thread
        del self.worker

    def start(self):
        self.thread = QThread()
        self.worker = self.Worker(self.ml)
        self.go.connect(self.worker.start)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        print("Starting")
        self.go.emit()

class EventCounter(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.cLock = QMutex()
        self.c = 0

    def __del__(self):
        del self.cLock

    def up(self):
        self.cLock.lock()
        self.c += 1
        self.cLock.unlock()

    def get(self):
        self.cLock.lock()
        v = self.c
        self.cLock.unlock()
        return v

    def down(self):
        self.cLock.lock()
        self.c -= 1
        self.cLock.unlock()

    def checkAndDown(self):
        self.cLock.lock()
        res = bool(self.c)
        if res: self.c -= 1
        self.cLock.unlock()
        return not res

class Pulse(QObject):

    sink_manager = Manager()
    input_manager = Manager()

    inputEvCounter = EventCounter()

    _pa_ctx = None

    @staticmethod
    def _upsert_manage(t, manager, i):
        if bool(i) is False: return
        manager.upsert_item(t(i.contents))

    def _sink_info(self, ctx, sink_info, eol, ud):
        self._upsert_manage(Sink, self.sink_manager, sink_info)

    def _input_info(self, ctx, input_info, eol, ud):
        self._upsert_manage(Input, self.input_manager, input_info)

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
                                    self._c_ctx_sub_success, None)
            print ("Ready!")

    def _request_sinks(self, ctx, event=None):
        pa.pa_context_get_sink_info_list(ctx, self._c_sink_info, event)

    def _request_sink_state(self, ctx, id, event=None):
        pa.pa_context_get_sink_info_by_index(ctx, id, self._c_sink_info, event)

    def _request_inputs(self, ctx, event=None):
        pa.pa_context_get_sink_input_info_list(ctx, self._c_input_info, event)

    def _request_input_state(self, ctx, id, event=None):
        pa.pa_context_get_sink_input_info(ctx, id, self._c_input_info, event)

    def __init__(self, ml):
        QObject.__init__(self, ml)
        self._c_ctx_sub_success = pa.pa_context_success_cb_t( self._ctx_sub_success )
        self._c_ctx_sub_cb      = pa.pa_context_subscribe_cb_t( self._ctx_sub_cb )
        self._c_ctx_state       = pa.pa_context_notify_cb_t( self._ctx_state )
        self._c_ctx_event       = pa.pa_context_event_cb_t( self._ctx_event )
        self._c_sink_info       = pa.pa_sink_info_cb_t( self._sink_info )
        self._c_input_info      = pa.pa_sink_input_info_cb_t( self._input_info )

        self._pa_ctx = pa.pa_context_new(ml.get_api(), c.c_char_p(b'Py_tray_mixer'))

        rt = pa.pa_context_connect(self._pa_ctx, None, pa.PA_CONTEXT_NOFLAGS, None)

        rt = c.c_int()

        pa.pa_context_set_event_callback(self._pa_ctx, self._c_ctx_event, None)
        pa.pa_context_set_state_callback(self._pa_ctx, self._c_ctx_state, None)

    def _del__(self):
        pa.pa_context_disconnect(self._pa_ctx)

    @pyqtSlot(int, bool)
    def setSinkMute(self, index, val):
        pa.pa_context_set_sink_mute_by_index(self._pa_ctx, index, int(val),
                                             self._c_ctx_sub_success, None)

    @pyqtSlot(int, int)
    def setSinkVolume(self, index, index):
        pass

    @pyqtSlot(int, bool)
    def setInputMute(self, index, val):
        pa.pa_context_set_sink_input_mute(self._pa_ctx, index, int(val),
                                          self._c_ctx_sub_success, None)

    @pyqtSlot(int, int)
    def setInputVolume(self, index, val):
        pass
