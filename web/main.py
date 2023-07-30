import asyncio
import subprocess
import json
import base64
import zipfile
import shutil
import re
from os import getenv
from pathlib import Path
from io import BytesIO
from mitmproxy import options
from mitmproxy.tools import dump
from mitmproxy.http import HTTPFlow
from Crypto.Cipher import AES
import threading
import _thread
from win32com.client import GetObject
import os
import signal
import sys
import webbrowser

"""
This program export encrypted books from read.e-vrit.co.il and decrypt them
Please don't use this to pirate books

You must install chrome browser
navigate to the book you want to download, open it and it will be downloaded automatically
then you can open and read it with https://calibre-ebook.com/ and also you can convert it to PDF using calibre
"""


APP_URL = 'https://read.e-vrit.co.il/main'
PROXY_HOST = 'localhost'
PROXY_PORT = 8090


def signal_handler(sig, frame):
    ChromeLauncher.stop_chrome()
    sys.exit(0)

class ChromeLauncher:
    def launch(self):
        path = self.stop_chrome()
        if not path:
            path = self._find_chrome_path()
        cmd = [
            path,
            f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}',
            '--ignore-certificate-errors',
            '--disable-application-cache',
            '--new-window',
            APP_URL
        ]

        # Wait for chrome to exit
        # when chrome exit interrupt the script
        proc = subprocess.Popen(cmd, shell=True)
        def wait_for_proc():
            proc.wait()
            _thread.interrupt_main()
        threading.Thread(target=wait_for_proc, daemon=True).start()


    def _find_chrome_path(self):
        win_paths = [
            Path(getenv(var)) / 'Google/Chrome/Application/chrome.exe' for var in 
            ('ProgramFiles', 'ProgramFiles(x86)', 'LocalAppData')
        ]
        for path in win_paths: 
            if path.exists():
                return path
        if sys.platform == 'win32':
            webbrowser.open_new_tab('https://www.google.com/chrome/')
            raise Exception('Cant find chrome! Install first')
        # Linux
        return shutil.which('google-chrome')

    @staticmethod
    def stop_chrome():
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        process_list = [
            (p.Properties_("ProcessID").Value, p.Properties_("Name").Value, p.Properties_("ExecutablePath").Value) 
            for p in processes
        ]
        for proc in process_list:
            pid, name, path = proc
            if name.lower() == 'chrome.exe':
                os.kill(pid, signal.SIGINT)
                return path


class BookDecryptor:
    def __init__(self, book_b64, key):
        self.book_b64 = book_b64
        self.key = key.encode('utf-8')
        self.title = 'book'

    def decrypt_book(self):
        self.book = self._extract_book()
        self._decrypt_pages()
        self._fix_font_size()
        self._extract_title()
        self._write_decrypted_epub()
        self._cleanup()

    def _extract_book(self):
        book = base64.b64decode(self.book_b64)
        zf = zipfile.ZipFile(BytesIO(book))
        return {name: zf.read(name) for name in zf.namelist()}
    
    def _decrypt_pages(self):
        for name, data in self.book.items():
            if not name.endswith('.xhtml'):
                continue
            cipher = AES.new(self.key, AES.MODE_CBC)
            dec = cipher.decrypt(data)
            
            try:
                dec = dec[dec.index(b'<!DOCTYPE'): dec.index(b'</html>') + 7]
                dec = b'<?xml version="1.0"?>\n' + dec
            except Exception:
                pass
            self.book[name] = dec

    def _fix_font_size(self):
        for name, data in self.book.items():
            if not name.endswith('idGeneratedStyles.css'):
                continue
            data += b"""\n
            p {
                font-size: 2em;
                padding: 12px;
            }
            """
            self.book[name] = data

    def _extract_title(self):
        for name, data in self.book.items():
            if not name.endswith('content.opf'):
                continue
            title_re = re.search(b'<dc:title>(.+)</dc:title>', data)
            if title_re:
                self.title = title_re.group(1)
                self.title = self.title.decode('utf-8')
            data = re.sub(b'data-username="[^"]+"', b'', data)
            self.book[name] = data

    def _write_decrypted_epub(self):
        with zipfile.ZipFile(f'{self.title}.epub', "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path, data in self.book.items():
                if file_path.endswith('/'):
                    continue
                zipf.writestr(file_path, data)

    def _cleanup(self):
        print(f'Written {self.title}.epub')


class JSInjector:
    def request(self, flow: HTTPFlow) -> None:
        try:
            if 'sendBook' in flow.request.url:
                data = json.loads(flow.request.data.content)
                book_b64, key = data['book'], data['key']
                BookDecryptor(book_b64, key).decrypt_book()
        except Exception as e:
            print(e)
    def response(self, flow: HTTPFlow):
        try:
            # Disable cache
            headers = flow.response.headers
            headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            headers['Expires'] = '0'
            headers['Pragma'] = 'no-cache'

            # inject js code
            if '5.e78ff86c.chunk.js' in flow.request.url:
                print('Injecting JS')
                pattern = b"function(_0x32c239,_0x16d30a){"
                script = b"""
const key = _0x4a8346.current.bookKey
if (!window?.sentKeys) {
    window.sentKeys = []
}
if (!window.sentKeys.includes(key)) {
    fetch('http://localhost:8090/sendBook', {method: 'POST', body: JSON.stringify({
        key: _0x4a8346.current.bookKey,
        book: _0xa0a9d4
    })})
    window.sentKeys.push(key)
}
                """
                replace_to = pattern + b'\n' + script + b';'
                flow.response.content = flow.response.content.replace(pattern, replace_to)
        except Exception as e:
            print(e)


class Proxy:
    def __init__(self) -> None:
        self.opts = options.Options(listen_host=PROXY_HOST, listen_port=PROXY_PORT, ssl_insecure=True)

    async def start(self):
        master = dump.DumpMaster(
            self.opts,
            with_termlog=False,
            with_dumper=False,
        )
        master.addons.add(JSInjector())
        
        await master.run()
        return master

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    ChromeLauncher().launch()
    asyncio.run(Proxy().start())
