import ctypes
from argparse import ArgumentParser
from atexit import register
from os import rmdir, remove, makedirs, listdir, system, _exit
from random import randint, uniform
from threading import Thread, enumerate
from time import sleep

from requests import head, get
from termcolor import cprint, colored
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

ap = ArgumentParser('Thread Downloader', 'Download files quickly.',
                    '''This is a thread downloader.\nYou can use it Download large file quickly.''')
ap.add_argument('--URL', '-u', type=str, required=True, help='URL')
ap.add_argument('--dir', '-d', type=str, required=True, help='Download dir')
ap.add_argument('--thread-num', '-t', type=int, required=False, default=16, help='Thread num')
meg = ap.add_mutually_exclusive_group()
meg.add_argument('--shut', '-S', action='store_true', required=False,
                 help='Use "shutdown /p" to shutdown your computer.')
meg.add_argument('--sleep', '-s', action='store_true', required=False, help='Use "shutdown /h" to sleep your computer.')
meg.add_argument('--reboot', '-r', action='store_true', required=False,
                 help='Use "shutdown /r /t 0" to reboot your computer.')
ap.add_argument('--no-ssl-verify', action='store_false', required=False, help='Skip SSL verify')
ap.add_argument('--http-proxy', type=str, required=False, default=None)
ap.add_argument('--https-proxy', type=str, required=False, default=None)
args = vars(ap.parse_args())
del ap, meg


def download(url: str, _from: int, to: int, id):
    global rates, FILE
    rates.append(0)
    reponse = get(url, headers={'Range': f"bytes={_from}-{to}",
                                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"},
                  stream=True, verify=args['no_ssl_verify'],
                  proxies={'http': args['http_proxy'], 'https': args['https_proxy']})
    if reponse.ok:
        try:
            length = int(reponse.headers['Content-Length'])
            with open(TMPDIR + f'\\{id}', 'wb+', buffering=0) as file:
                finished = 0
                for ch in reponse:
                    finished += file.write(ch)
                    rates[id] = finished / length
                reponse.close()
        except Exception as err:
            cprint(f"\n\nError:{err}", 'red')
            _exit(1)
    else:
        cprint(f'\n\nError:{reponse.status_code} {reponse.reason}', 'red')
        _exit(1)


def threads():
    i = -1
    for i in range(0, args.get('thread_num') - 1):
        start, end = i * ONELENGTH, (i + 1) * ONELENGTH
        t = Thread(target=download, args=(reponse.url, start, end - 1, i), daemon=True)
        t.start()
        sleep(uniform(0, 2))
    start, end = i * ONELENGTH, (i + 1) * ONELENGTH
    t = Thread(target=download, args=(reponse.url, ONELENGTH * (i + 1), LENGTH, i + 1))
    t.start()

    del i, t
    while True:
        for thread in enumerate():
            if not thread.is_alive(): thread.join()


def mktmpdir(downloaddir) -> str:
    seed = hex(randint(0x100000, 0x999999)).lstrip("0x")
    tmp_dir = downloaddir + f'\\.tmp\\{seed}'
    try:
        makedirs(tmp_dir)
        return tmp_dir
    except FileExistsError:
        return mktmpdir(downloaddir)


@register
def on_exit():
    if args.get('shut', False):
        system('shutdown /p')
    elif args.get('sleep', False):
        system('shutdown /h')
    elif args.get('reboot', False):
        system('shutdown /r /t 0')


disable_warnings(InsecureRequestWarning)

ctypes.windll.kernel32.SetThreadExecutionState(0x00000001)
register(ctypes.windll.kernel32.SetThreadExecutionState, ctypes.c_uint(0))

cprint('Finding file...', 'green')
reponse = head(args['URL'], allow_redirects=True, verify=args['no_ssl_verify'],
               proxies={'http': args['http_proxy'], 'https': args['https_proxy']})
if not reponse.ok:
    cprint(f'Error:{reponse.status_code} {reponse.reason}', 'red')
    _exit(1)
if reponse.headers.get('Accept-Ranges')=='bytes':
    cprint('Server support "Range" header.', 'green')
else:
    cprint('This server can\'t threading download.', 'red')
    _exit(1)
LENGTH = int(reponse.headers.get('Content-Length', 0))

v1 = reponse.url.rfind('/') + 1
v2 = reponse.url.rfind('?', v1)
if v2 == -1:
    _name = reponse.url[v1:].rstrip('?')
else:
    _name = reponse.url[v1:v2]
del v1, v2

name = input(colored(f'Please enter the file name[{_name}]:'))
if not name:
    FILENAME = _name
else:
    FILENAME = name
del name, _name

print('File found:' + colored(f'{FILENAME}', "blue"), 'Size:' + colored(f'{LENGTH} B', 'blue'),
      'Type:' + colored(f'{reponse.headers.get("Content-Type")}', 'blue'), sep='\n')
if LENGTH == 0:
    cprint('URL is not right.', 'red')
    _exit(1)
ONELENGTH = (LENGTH - 1) // args.get('thread_num')

TMPDIR = mktmpdir(args.get('dir'))

# print(f"Progress(downloading):{0.0:.2f}%[", colored(f"{' ' * 50}", 'green'), "]", sep='', end='\r')
rates = []

Thread(target=threads, daemon=True).start()
while True:
    try:
        rate = sum(rates) / args['thread_num']
    except ZeroDivisionError:
        rate = 0.0
    print(f"Progress(downloading):{rate * 100:.2f}%[", colored(f"{round(rate * 50) * '—': <50}", 'green'),
          f"]{len(enumerate()) - 2} threads", sep='', end='\r')
    if rate == 1: break
cprint('\nDownloading is over.', 'green')

mfile = open(args.get('dir') + '\\' + FILENAME, 'wb', buffering=0)
for i in range(0, listdir(TMPDIR).__len__()):
    sfile = open(TMPDIR + '\\' + str(i), 'rb')
    finished = 0
    while True:
        data = sfile.read(1048576)
        if not data: break
        finished += mfile.write(data)
        rate = finished / LENGTH
        print(f"Progress(copying {i + 1}/{args['thread_num']}):{rate * 100:.2f}%[",
              colored(f"{round(rate * 50) * '—': <50}", 'green'), "]",
              sep='', end='\r')
    sfile.close()
    remove(sfile.name)
    mfile.flush()
try:
    rmdir(TMPDIR)
    rmdir(args.get('dir') + '\\.tmp')
except OSError:
    cprint('\nTemp dir can\'t remove.', 'yellow')
cprint('\nCopying is over.', 'green')
cprint('\nAll is over.', 'green')
