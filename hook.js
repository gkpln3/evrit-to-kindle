   
console.log("Script loaded successfully ");
Java.perform(function x() { //Silently fails without the sleep from the python code
    console.log("Inside java perform function");
    //get a wrapper for our class
    var my_class = Java.use("e.c.h.b");
    //replace the original implmenetation of the function `fun` with our custom function
    my_class.a.implementation = function (a1, a2, a3, a4) {
        //print the original arguments
        // console.log("original call: fun(" + x + ", " + y + ")");
        //call the original implementation of `fun` with args (2,5)

        var ret_value = this.a(a1, a2, a3, a4);
		send(ret_value);
        return ret_value;
    }
});