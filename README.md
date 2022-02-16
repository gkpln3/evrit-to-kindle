# evrit-book-decryptor
Decrypts encrypted books from Ivrit to allow sending them to Kindle devices, Please don't use this to pirate books.

Evrit stores its EPUB files in the `/data/data/com.yit.evritViewer/files/Books` folder, each epub file (which is basically a `zip`) holds a couple of `xhtml` files (one for each chapter), evrit encrypts those files (inside the `zip`) and stores them under the same name, on startup it decrypts them back and uses the decrypted file.

# How
Open evrit apk using jeb or something similar, look for this string: "AES/CBC/PKCS7Padding" to find the following function:

<img width="446" alt="Screen Shot 2022-02-17 at 1 08 35" src="https://user-images.githubusercontent.com/8081679/154372781-c7705c37-80c8-4219-b6f6-6e5494b21ca4.png">

The return value of this function is the decrypted `xhtml` file, run the frida script to get the decrypted copies, replace the original `xhtml` files in the epub file and repack, and viola.
Have fun.

Also, don't pirate books.
