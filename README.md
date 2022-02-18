# evrit-book-decryptor
Decrypts encrypted books from Ivrit to allow sending them to Kindle devices, Please don't use this to pirate books.

Evrit stores its EPUB files in the `/data/data/com.yit.evritViewer/files/Books` folder, each epub file (which is basically a `zip`) holds a couple of `xhtml` files (one for each chapter), evrit encrypts those files (inside the `zip`) and stores them under the same name, on startup it decrypts them back and uses the decrypted file.

# How to use
Get a rooted Android phone with frida (or inject frida-gadget into evrit's APK without rooting your phone).

Create a directory called `book`
```sh
mkdir book
```

Run `loader.py`
```sh
python3 loader.py
```

Make sure the book is not open in the evrit app, and that it is scrolled to the first page.

Open the book in evrit app with the frida script attached.

Unzip the original epub file (found under `/data/data/com.yit.evritViewer/files`)

Replace all `xhtml` files from the encrypted epub with the decrypted ones under the `books` folder.

Pack the epub back into a `zip` file and change it's extension to `.epub`

If you want to upload the file to kindle, use any tool to convert the epub to azw3 format (mobi doesn't support Hebrew well) and then copy the azw3 file to your kindle (using USB, doesn't work by sending it via email for some reason).

Have fun!

# How does it work
Open evrit apk using jeb or something similar, look for this string: "AES/CBC/PKCS7Padding" to find the following function:

<img width="446" alt="Screen Shot 2022-02-17 at 1 08 35" src="https://user-images.githubusercontent.com/8081679/154372781-c7705c37-80c8-4219-b6f6-6e5494b21ca4.png">

The return value of this function is the decrypted `xhtml` file, run the frida script to get the decrypted copies, replace the original `xhtml` files in the epub file and repack, and viola.
Have fun.

Also, don't pirate books.
