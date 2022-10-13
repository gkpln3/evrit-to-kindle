
console.log("Script loaded successfully ");
Java.perform(function x() { // Silently fails without the sleep from the python code
    console.log("Inside java perform function");
    // TODO: This doesnt work for now, need to update.
    // var my_class = Java.use("e.c.g.a.b");
    // my_class.a.implementation = function (a1) {
    //     var ret_value = this.a(a1);
	// send({'name': a1, 'data': ret_value});
    //     return ret_value;
    // }

    // Disable root detector...
    var root_detector = Java.use("o.mode$read");
    root_detector.putInt.implementation = function (key, value) {
        if (key.includes("key_device_blocked")) {
            console.log("Bypassing root detection");
            return this.putInt(key, -1);
        }
        return this.putInt(key, value);
    }

});
