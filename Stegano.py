
from PIL import Image, ImageChops
import math
import random as rd


class Stegano:

    @staticmethod
    def update_lsb(lsb, dst):
        if lsb == 0 and dst == '1':
            return 1
        elif lsb == 1 and dst == '0':
            return -1
        return 0

    @staticmethod
    def encode(fimg, fmsg, key):
        # membaca file pesan
        with open(fmsg, 'r') as f:
            msg = f.read()
            len_msg = len(msg)*8  # 1 karakter = 8 bit

        # membaca gambar
        img = Image.open(fimg)
        img_bytes = bytearray(img.tobytes())

        # mempersiapkan header
        # cap_header : panjang bit maksimal untuk memetakan bit dari panjang pesan
        cap_header = math.ceil(math.log(len(img_bytes), 2))

        # capacity : panjang bit maximal yang digunakan untuk memetakan bit dari pesan
        capacity = len(img_bytes) - cap_header
        header = bin(len_msg)[2:]

        if capacity < len_msg:
            return False

        # acak posisi berdasarkan kunci
        suffle_index = [e for e in range(len(img_bytes))]
        seed = 1
        for x in key:
            seed *= ord(x)
        seed = seed % len(img_bytes)
        rd.seed(seed)
        rd.shuffle(suffle_index)

        # menulis header ke pixel gambar
        # karena cap_header adalah panjang bit maximal anda kondisi cap_header tidak digunakan seluruhnya
        # maka dengan menambahkan prefix bit "0" maka tidak akan mengubah arti dari header
        cap_header_unused = cap_header-len(header)
        prefix = "0"*cap_header_unused
        header = prefix + header

        # manipulasi lsb untuk header
        for i in range(cap_header):
            lsb = img_bytes[suffle_index[i]] % 2
            dst = header[i]
            img_bytes[suffle_index[i]] += Stegano.update_lsb(lsb, dst)

        # manipulasi lsb untuk pesan
        current = cap_header
        for char in msg:
            char_bytes = "{0:08b}".format(ord(char))
            for b in char_bytes:
                lsb = img_bytes[suffle_index[current]] % 2
                img_bytes[suffle_index[current]] += Stegano.update_lsb(lsb, b)
                current += 1

        # menyimpan stegano-image
        fout = Image.frombytes(img.mode, img.size, bytes(img_bytes))
        fout_name = img.filename.rsplit('\\', 1)[-1]
        path = img.filename.split("\\")
        path[-1] = 'stegano_'+fout_name
        fout.save('\\'.join(path))

        print("Success...")

        return True

    @staticmethod
    def decode(fimg, fmsg, key):
        # membaca gambar
        img = Image.open(fimg)
        img_bytes = bytearray(img.tobytes())

        # mencari suffle index berdasarkan kunci
        suffle_index = [e for e in range(len(img_bytes))]
        seed = 1
        for x in key:
            seed *= ord(x)
        seed = seed % len(img_bytes)
        rd.seed(seed)
        rd.shuffle(suffle_index)

        # memisahkan header dengan data
        cap_header = math.ceil(math.log(len(img_bytes), 2))
        # membaca bit dari header
        header = ''.join([str(img_bytes[suffle_index[i]] % 2)
                          for i in range(cap_header)])
        len_msg = int(header, 2)

        # mengekstrak pesan dari gambar
        char = ''
        msg = []
        for i in range(cap_header, cap_header+len_msg):
            lsb = str(img_bytes[suffle_index[i]] % 2)
            char += lsb
            if len(char) == 8:
                assci_code = int(char, 2)
                msg.append(chr(assci_code))
                char = ''

        # menulis pesan ke file
        with open(fmsg, 'w') as f:
            fmsg = ''.join(msg)
            print(fmsg)
            f.write(fmsg)

        print("Success...")

        return True


def main():
    import sys
    if len(sys.argv) in range(4, 6):
        task = sys.argv[1]
        f1 = sys.argv[2]
        f2 = sys.argv[3]
        opt = sys.argv[4]

        if task == '--encode':
            Stegano.encode(f1, f2, opt)
        elif task == '--decode':
            Stegano.decode(f1, f2, opt)
        elif task == '--compare':
            img = ImageChops.difference(Image.open(f1), Image.open(f2))
            img.save(opt)
            print("Success...")
    else:
        doc = """help:
        Encode (Menyembunyikan pesan ke gambar.)
        --------------------------------------------------
        command :
            stegano --encode path_img path_msg key

        Decode (Mengekstrak pesan dari gambar.)
        --------------------------------------------------
        command :
            stegano --encode path_img path_msg_out key

        Compare (Membandingkan dua gambar)
        --------------------------------------------------
        command :
            stegano --compare path_img1 path_img2 path_img_out
        """
        print(doc)
        return


if __name__ == "__main__":
    main()
