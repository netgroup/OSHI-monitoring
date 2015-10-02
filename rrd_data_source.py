class RRDDataSource(object):
    name = ""
    data_source_type = ""
    heartbeat = ""
    temp_value = 0

    def __init__(self, name, data_source_type, heartbeat, temp_value=None):
        self.name = name
        self.data_source_type = data_source_type
        self.heartbeat = heartbeat
        self.temp_value = temp_value
