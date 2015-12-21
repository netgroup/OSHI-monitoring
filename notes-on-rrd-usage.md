# Notes of the usage of .rrd files
We can query a RRD file with differents library function of RRDTOOL.

We can ask the time instace of the last and first update with two functions:

$ rrdtool last filename.rrd
$ rrdtool first filename.rrd

We can ask the value of the last update with funtion LASTUPDATE.

$ rrdtool lastupdate filename.rrd

In our case we have the values of the respectly entities:

rx_packet sdn_tx_packet rx_bytes sdn_rx_packet tx_bytes sdn_rx_bytes sdn_tx_byte tx_packet, and respectly values.

We can decide to export the RRD file in XML file:

$ rrdtool dump filename.rrd filename.xml.

If we omit a name of xml file, it prints to standard output the xml file.

WE can get data of the AVERAGE with the function "FETCH":

$ rrdtool fetch filename.rrd AVERAGE -r 30s -s -1h

Where -r is the resolution in seconds, -s is the start time of the fetch.
we can to express the time or in seconds, or in hours(h) or in minuts whith(m) or in specific second value since epoch(1970-01-01).

For other uses we can find infomation on http://oss.oetiker.ch/rrdtool/doc/index.en.html.