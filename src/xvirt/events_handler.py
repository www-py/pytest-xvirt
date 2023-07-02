from xvirt.events import EvtCollectionFinish, EvtRuntestLogreport


def make(file_path, path, parent):
    def events_handler(read_event):
        evt_cf = read_event()
        assert isinstance(evt_cf, EvtCollectionFinish)
        from xvirt.collectors import VirtCollector
        result = VirtCollector.from_parent(parent, name=file_path.name)
        result.nodeid_array = evt_cf.node_ids

        # report phase
        config = parent.config
        recv_count = 0
        while recv_count < len(evt_cf.node_ids):
            evt_rep = read_event()
            assert isinstance(evt_rep, EvtRuntestLogreport)
            rep = config.hook.pytest_report_from_serializable(config=config, data=evt_rep.data)
            config.hook.pytest_runtest_logreport(report=rep)
            recv_count += 1

        return result

    return events_handler
