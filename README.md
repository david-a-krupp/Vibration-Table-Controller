# Vibration Table Controller (Raspberry Pi 4)

System aligned to Raspberry Pi OS, MCC UL for Linux (uldaq), and gpiozero.
Includes an optional ±10 V line driver for amplifiers that need bipolar drive.

## Features
- Control modes: Manual, Sine Sweep, Random, Sine-on-Random (SoR), Resonance Dwell, Shock
- Safety state machine (INIT, MUTED, ARMED, RUNNING; faults, MUTED)
- Real-time plots using PyQtGraph
- CSV logging with metadata
- **Manual USB export** of current run logs and a SS of the plot
- Touch UI scaling, full-screen toggle for 7" Raspberry Pi display
- Autostart using systemd

## Install
```bash
sudo apt update
sudo apt install -y python3-pip python3-gpiozero python3-pyqt5 libuldaq
pip3 install -r requirements.txt
```

## Run
```bash
python3 app.py
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
- Plug in a USB stick. It should auto-mount under `/media/pi/<label>` 
- Press **Export** in the UI, select your mount, and the app should copy the current CSV log and a PNG plot SS.

## Hardware notes
- MCC USB-1208FS-Plus provides 0–5 V AO. Use the included line driver design if ±10 V is required.
- Use a 5 V opto-isolated relay for mute. Default state is MUTED (LOW).
- Protect the ADS1115 with divider + RC + series resistor. Consider differential mode.
- E-stop switch should be wired to a dedicated GPIO input and monitored in software (gpio.py).

## Calibration
Adjust values in vtc/config.py.
Use the Loopback Calibration routine to compute effective gain/scale for your DAC/ADC chain.
