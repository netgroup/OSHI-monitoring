class RRDDataSource(object):
    name = ""
    data_source_type = ""
    heartbeat = ""

    def __init__(self, name, data_source_type, heartbeat):
        self.name = name
        self.data_source_type = data_source_type
        self.heartbeat = heartbeat
