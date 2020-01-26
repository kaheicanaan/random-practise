from typing import Tuple
import re
import requests
import socket


def decode_line(input_line: bytes) -> str:
    """
    Lines that cannot be parsed using utf-8 are:

    b'128.159.144.83 - - [14/Aug/1995:15:51:37 -0400] "\x16\xb1\x02\x896\x9e\x02\xffT7\x89F\x10\xc3\xc7F\x10\x01" 400 -\n'
    b'128.159.144.83 - - [14/Aug/1995:15:51:58 -0400] "\x16\xb1\x02\x896\x9e\x02\xffT7\x89F\x10\xc3\xc7F\x10\x01" 400 -\n'
    b'128.159.144.83 - - [14/Aug/1995:15:52:23 -0400] "\x16\xb1\x02\x896\x9e\x02\xffT7\x89F\x10\xc3\xc7F\x10\x01" 400 -\n'
    b'128.159.144.83 - - [14/Aug/1995:15:59:35 -0400] "\x16\xb1\x02\x896\x9e\x02\xffT7\x89F\x10\xc3\xc7F\x10\x01" 400 -\n'
    b'worm.hooked.net - - [18/Aug/1995:11:34:45 -0400] "GET /shuttle/countdown/dy \x80?status%20report HTTP/1.0" 404 -\n'
    b'128.159.117.22 - - [30/Aug/1995:13:45:35 -0400] "\xfd\xd1\xed.\x8a\x0b2\xed.\x8b>\xee .\x8a\x032\xe4\xd1\xe5\xe9\xe2\xfd\xbd\xff\xff\xc3.\xc7\x06\xe2 " 400 -\n'
    b'163.206.42.13 - - [31/Aug/1995:11:04:42 -0400] "\x80|\x05\x11t\x03\xb09\xc3\xb0\'\xc3\x80|\x05\x11u\x0b&\xf7G\x18\x01" 400 -\n'
    b'163.206.42.13 - - [31/Aug/1995:11:04:49 -0400] "\x80|\x05\x11t\x03\xb09\xc3\xb0\'\xc3\x80|\x05\x11u\x0b&\xf7G\x18\x01" 400 -\n'
    b'port9.trytel.com - - [31/Aug/1995:13:19:14 -0400] "GET /facts\xe9faq12.html HTTP/1.0" 404 -\n'
    b'128.159.117.22 - - [31/Aug/1995:14:49:09 -0400] "\xfd\xd1\xed.\x8a\x0b2\xed.\x8b>\xee .\x8a\x032\xe4\xd1\xe5\xe9\xe2\xfd\xbd\xff\xff\xc3.\xc7\x06\xe2 " 400 -\n'

    Everything okay except for the request content (which is not related to the question). Just ignore those words.
    :param input_line:
    :return:
    """
    return input_line.decode('utf-8', errors='ignore')


def parser_log(input_line: bytes) -> Tuple[str, str, str, str, str]:
    line = decode_line(input_line)
    # print(line)
    regex = r'(\S+) - - \[(.*)\] "(.*)" (\S+) (\S+)'
    return re.search(regex, line).groups()


def map_host_to_country(host_or_ip: str) -> str:
    """
    'http://api.hostip.info/country.php' might return 'XX' if country info is unknown
    :param host_or_ip:
    :return:
    """
    try:
        # first get IP by host
        ip_address = socket.gethostbyname(host_or_ip)
        # then found country according to it IP
        url = 'http://api.hostip.info/country.php'
        response = requests.post(url, data={'ip': ip_address})
        country = response.content.decode('utf-8')
        return country
    except socket.gaierror:
        return 'XX'
