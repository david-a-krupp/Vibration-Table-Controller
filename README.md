# Vibration Table Controller (Raspberry Pi 4)

## Features
- Control modes: Manual, Sine Sweep, Random, Sine-on-Random (SoR), Resonance Dwell, Shock
- Safety state machine (INIT, MUTED, ARMED, RUNNING; faults, MUTED)
- Real-time plots using PyQtGraph
- CSV logging with metadata
- **Manual USB export** of current run logs and a SS of the plot
- Touch UI scaling, full-screen toggle for 7" Raspberry Pi display
- Autostart using systemd

## Run
```bash
cd ~/Vibration-Table-Controller
source venv/bin/activate
python app.py
```

## Autostart (systemd)
```bash
sudo mkdir -p /opt/vtc
sudo cp *.py /opt/vtc/
sudo cp vibration-controller.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vibration-controller
sudo systemctl start vibration-controller
```

## USB export
- Plug in a USB drive to one of the Raspberry Pi ports. It should auto-mount under `/media/pi/<label>` 
- Press **Export** in the UI, select your mount, and the app should copy the current CSV log and a PNG plot SS.

## Calibration
Adjust values in vtc/config.py.
Use the Loopback Calibration routine to compute effective gain/scale for the DAC/ADC chain.
