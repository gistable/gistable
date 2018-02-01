#!/usr/bin/env python
import argparse
import qrcode


def main():
    parser = argparse.ArgumentParser(description='Generate QR code for OTP.')
    parser.add_argument('user', nargs=1)
    parser.add_argument('key', nargs=1)
    parser.add_argument('issuer', nargs=1)
    args = parser.parse_args()

    otp_value = 'otpauth://totp/{2}:{0}?secret={1}&issuer={2}' \
        .format(args.user[0], args.key[0], args.issuer[0])

    qr = qrcode.QRCode(box_size=4, border=4)
    qr.add_data(otp_value)
    qr.make(fit=True)

    with open('qrcode.jpg', 'w') as f:
        qr.make_image().save(f)


if __name__ == '__main__':
    main()
