
console.log("Script loaded successfully ");
Java.perform(function x() { // Silently fails without the sleep from the python code
    console.log("Inside java perform function");
    var my_class = Java.use("e.c.g.a.b");
    my_class.a.implementation = function (a1) {
        var ret_value = this.a(a1);
	send({'name': a1, 'data': ret_value});
        return ret_value;
    }
});
