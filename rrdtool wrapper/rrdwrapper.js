exec = require('child_process').exec;
spawn = require('child_process').spawn;

var DS_TYPE = {
	GAUGE : 'GAUGE',
	COUNTER : 'COUNTER',
	DERIVE : 'DERIVE',
	ABSOLUTE : 'ABSOLUTE'
};

var RRA_TYPE = {
	AVERAGE : 'AVERAGE',
	MIN : 'MIN',
	MAX : 'MAX',
	LAST : 'LAST'
};

module.exports.DS_TYPE = DS_TYPE;
module.exports.RRA_TYPE = RRA_TYPE;

exports.now = function(){
	return Math.ceil((new Date).getTime() / 1000);
};

exports.DS = function(ds_name, ds_type, heartbeat, min, max){
	return "DS:" + ds_name + ":" + ds_type.toString() + ":" + heartbeat + ":" + min + ":" + max;
};

exports.DS_Compute = function(ds_name, rpn_expression){
	return "DS:" + ds_name + ":COMPUTE:" + rpn_expression;
};

exports.RRA = function(rra_type, xff, steps, rows){
	return "RRA:" + rra_type.toString() + ":" + xff + ":" + steps + ":" + rows;
};

exports.create = function(filename, start_time, step, DS, RRAs){
	var cmdArgs = ["create", filename, "--start", start_time, "--step", step, DS].concat(RRAs);

	console.info("Command argument: rrdtool " + cmdArgs.join(" "));

	var process = spawn("rrdtool", cmdArgs);
};
