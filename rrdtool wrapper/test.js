var os = require('os');
var filename = 'test.rrd';
var rrd = require('./rrdwrapper');

var filename = "temp.rrd";
var ds = rrd.DS("busy", rrd.DS_TYPE.GAUGE, 120, 0, "U");
var rra1 = rrd.RRA(rrd.RRA_TYPE.LAST, 0.5, 1, 60);
var rra2 = rrd.RRA(rrd.RRA_TYPE.AVERAGE, 0.5, 100, 10);

rrd.create(filename, rrd.now(), 300, ds, rra1);
