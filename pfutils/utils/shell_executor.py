import errno
import json
import os
import select
import signal
import struct
import six
from websocket import ABNF
import threading

class ShellExecutor(object):
    def __init__(self, k8s_stream=None, stdin=True):
        self.k8s_stream = k8s_stream
        self.master_fd = None
        self.stdin_flag = stdin

    def spawn(self):
        import pty
        import tty
        pid, master_fd = pty.fork()
        self.master_fd = master_fd
        if pid == pty.CHILD:
            os.execlp('bash', 'bash')

        if self.stdin_flag:
            old_handler = signal.signal(signal.SIGWINCH, self._signal_winch)
            mode = tty.tcgetattr(pty.STDIN_FILENO)
            tty.setraw(pty.STDIN_FILENO)

        self._init_fd()
        try:
            self._copy()
        except Exception as e:
            print(e)
            pass
            
        tty.tcsetattr(pty.STDIN_FILENO, tty.TCSAFLUSH, mode)

        self.k8s_stream.close()
        self.k8s_stream = None
        if self.master_fd:
            os.close(self.master_fd)
            self.master_fd = None
            
        if self.stdin_flag:
            signal.signal(signal.SIGWINCH, old_handler)

    def _init_fd(self):
        self._set_pty_size()

    def _signal_winch(self, signum, frame):
        self._set_pty_size()

    def _set_pty_size(self):
        import pty
        import fcntl
        import termios
        packed = fcntl.ioctl(
            pty.STDOUT_FILENO,
            termios.TIOCGWINSZ,
            struct.pack('HHHH', 0, 0, 0, 0),
        )
        rows, cols, h_pixels, v_pixels = struct.unpack('HHHH', packed)
        self.k8s_stream.write_channel(
            4,
            json.dumps({
                "Height": rows,
                "Width": cols,
            })
        )

    def _copy(self):
        import pty
        assert self.k8s_stream is not None
        k8s_stream = self.k8s_stream
        
        socks = [k8s_stream.sock.sock]
        
        if self.stdin_flag:
            socks += [pty.STDIN_FILENO]
        while True:
            try:
                rfds, wfds, xfds = select.select(socks, [], [], )
            except select.error as e:
                print('error')
                no = e.errno if six.PY3 else e[0]
                if no == errno.EINTR:
                    continue

            if self.stdin_flag and pty.STDIN_FILENO in rfds:
                data = os.read(pty.STDIN_FILENO, 1024)
                self.stdin_read(data)

            if k8s_stream.sock.sock in rfds:
                if k8s_stream.peek_stdout():
                    data = k8s_stream.read_stdout()
                    self.master_read(data)

                if k8s_stream.peek_channel(3):
                    return
                    
    def write_stdout(self, data):
        import pty
        os.write(pty.STDOUT_FILENO, data.encode())

    def write_master(self, data):
        assert self.k8s_stream is not None
        self.k8s_stream.write_stdin(data)

    def master_read(self, data):
        self.write_stdout(data)

    def stdin_read(self, data):
        self.write_master(data)