import time

import frida

device = frida.get_usb_device()
pid = device.spawn(["com.yit.evritViewer"])
device.resume(pid)
time.sleep(1)  # Without it Java.perform silently fails
session = device.attach(pid)
with open("hook.js") as f:
    script = session.create_script(f.read())

count = 3
def handle_message(message, data):
	global count
	with open(f"book/IDIOTS-s-{count}.xhtml", "w") as f:
		f.write(message['payload'])
	count+=1
	# print(message['payload'])
script.on("message", handle_message)
script.load()

# prevent the python script from terminating
input()