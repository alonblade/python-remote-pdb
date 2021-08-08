# coding: utf-8

from time import time
from select import select
import sys
from bdb import BdbQuit

from remote_pdb import RemotePdb


class Wrapper:
    def __init__(self, s, dt=0.1):
        """
        s - already open socket
        """
        s.setblocking(0)
        self._file = s.makefile('rw')
        self._fd = s.fileno()
        self._s = s
        self.dt = dt
        self.count = 0

    def readline(self):
        print("readline called")
        buf = []
        while True:
            self.count += 1
            sys.stdout.write(f'\r{"".join(buf)}         {self.count:10}')
            sys.stdout.flush()
            res_read, x, y = select([self._fd], [], [], 0.1)
            if self._fd in res_read:
                new = self._file.read(1024)
                buf.append(new)
                if '\n' in new:
                    ret = ''.join(buf)
                    break
        return ret

    def write(self, b):
        # BLOCKING
        self._file.write(b)

    def flush(self):
        # BLOCKING ?
        self._file.flush()

    def close(self):
        self._s.close()


def acceptor(s, dt=0.1):
    count = 0
    s.setblocking(0)
    fd = s.fileno()
    while True:
        r, _a, _b = select([fd], [], [], dt)
        if fd in r:
            print("accepted socket")
            return s.accept()


if __name__ == '__main__':
    fd = sys.stdin.fileno()

    pdb = RemotePdb(host='0.0.0.0', port=51234, acceptor=acceptor, filewrapper_constructor=Wrapper)
    pdb.use_rawinput = 0
    try:
        pdb.set_trace()
    except BdbQuit:
        pass

