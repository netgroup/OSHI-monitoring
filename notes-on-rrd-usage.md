# Notes of the usage of .rrd files
A RRD file can be queried with different RRDTool library functions.

Time of the last and first updates:

$ rrdtool last filename.rrd
$ rrdtool first filename.rrd

Value of the last update with function lastupdate.

$ rrdtool lastupdate filename.rrd

In our case we have the values of the following data sources:

rx_packet sdn_tx_packet rx_bytes sdn_rx_packet tx_bytes sdn_rx_bytes sdn_tx_byte tx_packet.

Export a dump of the RRD file in XML format:

$ rrdtool dump filename.rrd filename.xml.

If you omit a name of xml file, it prints the output to standard output.

Get the AVERAGE with the function "FETCH":

$ rrdtool fetch filename.rrd AVERAGE -r 30s -s -1h

where -r is the resolution in seconds, -s is the start time of the fetch.

Time can be expressed in seconds (s), hours (h), minutes (m) or by specifying the number of seconds since epoch (1970-01-01).

Visit [RRDTool official site](http://oss.oetiker.ch/rrdtool/doc/index.en.html) for a more comprehensive documentation.
