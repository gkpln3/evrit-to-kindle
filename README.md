# Evrit Book Decryptor
Decrypts encrypted books from Evrit to allow sending them to Kindle devices.

**Don't use this to pirate books.**

# Update
This project doesn't work ATM, seems like they've changed the encryption method to use GCM instead of CBC.
Also they've added root detection, which is kind of a bummer because it makes the app unusable on some phones.
So I've updated the code with a root detection bypass, but didn't make it to update the decryptor itself (it also seems like evrit is not very happy with this project so I will not be updating it anytime soon).

# How to use
- Get a rooted Android phone with [frida-server](https://github.com/frida/frida/tags) (or inject `frida-gadget` into evrit's APK without rooting your phone).

- Open the evrit app and make sure all the books you want are present on the device (no cloud icon).

- Run `frida-server` on the target device.

- Run `loader.py`
```sh
python3 loader.py
```

- Open the book in evrit app, you will see the decrypted files as they are being fetched.

- If you want to upload the file to kindle, use any tool to convert the `epub` to `azw3` format (`mobi` doesn't support Hebrew well) and then copy the `azw3` file to your kindle (using USB, doesn't work by sending it via email for some reason).

Have fun!

Also, if you like a book, buy it, don't be a pirate.

# What to do if it breaks

Obfuscation is probably different.

Evrit stores its EPUB files in the `/data/data/com.yit.evritViewer/files/Books` folder, each epub file (which is basically a `zip`) holds a couple of `xhtml` files (one for each chapter), evrit encrypts those files (inside the `zip`) and stores them under the same name, on startup it decrypts them back and uses the decrypted file.
To find the decryption method we do the following:

- Open evrit apk using jeb or something similar, look for this string: `"AES/CBC/PKCS7Padding"` to find the following function:

<img width="446" alt="Screen Shot 2022-02-17 at 1 08 35" src="https://user-images.githubusercontent.com/8081679/154372781-c7705c37-80c8-4219-b6f6-6e5494b21ca4.png">

- It should have an xref from a function that looks something like this:

<img width="466" alt="Screen Shot 2022-02-18 at 22 18 18" src="https://user-images.githubusercontent.com/8081679/154755900-5fed20af-17e3-4212-aacd-821deb81c57f.png">

- The second function is our target, just fix the name in the `hook.js` file to match the new one.

You are also welcome to open a pull request.
