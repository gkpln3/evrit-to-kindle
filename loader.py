import time
import os
import frida
import tempfile
import glob
import shutil
import queue
import termcolor

tempdir = tempfile.mkdtemp()
decrypted_queue = queue.Queue()
def start_listening_for_decryptions():
	global tempdir
	device = frida.get_usb_device()
	pid = device.spawn(["com.yit.evritViewer"])
	device.resume(pid)
	time.sleep(1)  # Without it Java.perform silently fails
	session = device.attach(pid)
	with open("hook.js") as f:
		script = session.create_script(f.read())

	def handle_message(message, data):
		global tempdir
		if message["type"] == "error":
			raise Exception(message["description"])
		filename: str = message['payload']['name'][0]
		filename = filename[filename.find("com_yit_evrit"):]

		decrypted_queue.put({'name': filename, 'data': message['payload']['data']})
	script.on("message", handle_message)
	script.load()

def pull_files(source_dir: str, target_dir: str):
	if os.system(f"adb pull {source_dir} {target_dir} 2>/dev/null") != 0:
		# Failed to pull, probably need root.
		# Copy the files to /data/local/tmp and then pull them.
		os.system("adb shell su -c 'mkdir /data/local/tmp/evritDecryptor'")
		os.system(f"adb shell su -c 'cp -r {source_dir} /data/local/tmp/evritDecryptor'")
		if os.system(f"adb pull /data/local/tmp/evritDecryptor {target_dir}") != 0:
			raise Exception("Failed to pull files")

def download_encrypted_epubs() -> list:
	global tempdir
	print(f"Downloading epubs to {tempdir}")
	pull_files(f"/data/data/com.yit.evritViewer/files/Books/", tempdir)
	epubs = []
	for epub in glob.glob(f"{tempdir}/Books/*.epub"):
		print(f"Unpacking {epub}")
		extract_dir = epub.strip(".epub")
		shutil.unpack_archive(epub, format="zip", extract_dir=extract_dir)

		# Add extracted epub to the list of extracted epubs.
		epubs.append(extract_dir)

	return epubs

def get_encrypted_files(epub):
	def is_binary(f):
		return b'\x00' in open(f, 'rb').read()

	files = glob.glob(f"{epub}/OEBPS/*.xhtml")
	return [f for f in files if is_binary(f)]


def pack_finished_books():
	global epub_files

	for epub in list(epub_files.keys()):
		if len(epub_files[epub]) == 0:
			print(termcolor.colored(f"Got all files for {epub.split('/')[-1]}, repacking...", "green"))
			shutil.make_archive(f"{os.path.basename(epub)}", "zip", root_dir=epub)
			shutil.move(f"{os.path.basename(epub)}.zip", f"{os.path.basename(epub)}.epub")
			del epub_files[epub]
			print(termcolor.colored(f"Done", "green"))
	return len(epub_files) == 0

# prevent the python script from terminating
epubs = download_encrypted_epubs()

# Get a list of files to decrypt for each epub.
epub_files = {}
for epub in epubs:
	epub_files[epub] = get_encrypted_files(epub)


start_listening_for_decryptions()

while not pack_finished_books():
	try:
		decrypted_file = decrypted_queue.get()
		print(decrypted_file['name'], end="")
		decrypted_epub = decrypted_file['name'].split("/")[0]

		# Find relevant epub.
		epub = [e for e in epub_files.keys() if decrypted_epub in e][0]
		current_epub_files: list = epub_files[epub]
		current_file: str = [f for f in current_epub_files if decrypted_file['name'].split("/")[-1] in f][0]

		with open(current_file, "w") as f:
			f.write(decrypted_file['data'])
		current_epub_files.remove(current_file)
		epub_files[epub] = current_epub_files
		print(f" {len(current_epub_files)} remaining...")
		
	except IndexError as e:
		print()
		pass

print("All epubs finished")
