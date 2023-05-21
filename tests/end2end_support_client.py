tcp_port = 1234567890

# this file is run in inception-level-2; it is executed inside pytest that is executed inside a pytester

def pytest_xvirt_collect_file(file_path, path, parent):
    from xvirt.collectors import VirtCollector
    result = VirtCollector.from_parent(parent, name=file_path.name)
    result.nodeid_array = {nodeids_json}
    return result
