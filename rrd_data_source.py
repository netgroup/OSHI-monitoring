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

    def __str__(self):
        return "RRD Data Source(name=" + self.name + ", data_source_type=" + self.data_source_type + ", heartbeat=" \
               + self.heartbeat + ", temp_value=" + self.temp_value
