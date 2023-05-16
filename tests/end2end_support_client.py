tcp_port = 1234567890

def pytest_xvirt_collect_file(file_path, path, parent):
    from xvirt.collectors import VirtCollector
    result = VirtCollector.from_parent(parent, name=file_path.name)
    result.nodeid_array = {nodeids_json}
    return result
