import sys, time, threading
from PyQt5 import QtWidgets
from gui import MainWindow
from waveform import sine, sweep
from dac import output_waveform
from adc import read_channel
from safety import is_emergency
from logging import log_run

def run_profile(params):
    if params['mode'] == 'sine':
        t, wavedata = sine(params['f'], params['amp'], params['dur'])
    else:
        t, wavedata = sweep(params['f0'], params['f1'], params['amp'], params['dur'])
    readbacks = []
    fs = 2000  # Lower sample rate appropriate for 1208FS
    for i, val in enumerate(wavedata):
        if is_emergency():
            break
        output_waveform(0, 0, [val], fs)
        readbacks.append(read_channel(0))
        time.sleep(1.0 / fs)
    log_run('run.csv', t[:len(readbacks)], wavedata[:len(readbacks)], readbacks)

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.run_signal.connect(lambda p: threading.Thread(target=run_profile, args=(p,)).start())
    win.showFullScreen()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
