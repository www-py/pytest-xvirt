from xvirt import XVirt
from xvirt.events import EvtCollectionFinish, EvtRuntestLogreport, Evt


def _order_events2(xvirt_instance: XVirt):
    def re():
        event = xvirt_instance.recv_event()
        if event is None:
            return None
        return Evt.from_json(event)

    events = []
    while True:
        evt = re()
        if evt is None:
            yield None
            return

        if isinstance(evt, EvtCollectionFinish):
            yield evt
            break
        else:
            events.append(evt)

    for evt in events:
        yield evt

    while True:
        yield re()


def _order_events(xvirt_instance: XVirt):
    typed_events = []
    collection_finished_received = False

    def read_event():
        nonlocal collection_finished_received
        if collection_finished_received:
            if len(typed_events) == 0:
                return xvirt_instance.recv_event()
            else:
                return typed_events.pop(0)
        else:
            event = xvirt_instance.recv_event()
            if event is None:
                return None
            while True:
                evt = Evt.from_json(event)
                if isinstance(evt, EvtCollectionFinish):
                    collection_finished_received = True
                typed_events.append(evt)
                return event

    return read_event


def make(file_path, parent):
    def events_handler(xvirt_instance: XVirt):

        recv_event = _order_events2(xvirt_instance)
        evt_cf = next(recv_event)
        if evt_cf is None:  # this means that the user did not implement the remote side
            return None

        from xvirt.collectors import VirtCollector
        result = VirtCollector.from_parent(parent, name=file_path.name)
        result.nodeid_array = evt_cf.node_ids

        # report phase
        config = parent.config
        recv_count = 0
        while recv_count < len(evt_cf.node_ids):
            evt_rep = next(recv_event)
            assert isinstance(evt_rep, EvtRuntestLogreport)
            rep = config.hook.pytest_report_from_serializable(config=config, data=evt_rep.data)
            config.hook.pytest_runtest_logreport(report=rep)
            recv_count += 1

        xvirt_instance.finalize()
        return result

    return events_handler
