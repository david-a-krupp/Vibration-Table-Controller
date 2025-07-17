# Vibration-Table-Controller
Working repository for the creation of a vibration table controller intended for use in the University of Georgia SSRL Ling Dynamic Systems Vibration Table. This controller is specifically meant to pair with the HPA-K SP Amplifier and the V780 Vibrator System. This project was undertaken by David Krupp in order to fulfill MS in Engineering reqs.

---

**Project Objective**

Develop a modern, user-friendly controller to interface with the Ling Dynamic Systems V780 shaker and HPA-K amplifier. The system is intended for CubeSat flight qualification testing and supports:

- ±10 V analog waveform output
- GUI with touchscreen interface
- Emergency stop safety system
- Optional feedback monitoring (accelerometer or amp monitor)
- Real-time and logged data visualization
- CSV data export to USB

---

**System Components & Design Decisions**

- **Main Controller:** Raspberry Pi 5 for GUI control, logic, and data streaming  
- **Analog Output:** MCC USB-1208FS-Plus for ±10 V signal generation  
- **Feedback Monitoring:** ADS1115 16-bit I²C ADC  
- **Touch Display:** Waveshare 7" HDMI capacitive touchscreen  
- **Safety:** Hardware E-stop with relay cutoff  
- **Software Stack:** Python, PyQt5, mcculw, matplotlib, psutil  

---

**Bill of Materials (BoM)**

| Item                       | Description                                            | Est. Price |
|---------------------------|--------------------------------------------------------|------------|
| Raspberry Pi 5 (4GB)      | Main controller                                        | $60        |
| Waveshare 7” Touchscreen  | Touch interface via HDMI and USB                      | $65        |
| MCC USB-1208FS-Plus DAC   | ±10 V, 12-bit USB DAC                                 | $200       |
| ADS1115 ADC               | 16-bit I²C ADC for feedback signal                    | $15        |
| 2-Channel Relay Module    | Controls emergency shutdown                           | $4         |
| Emergency Stop Button     | NC/COM button for hard stop                           | $10        |
| 5V 5A USB-C Power Supply  | Power for Raspberry Pi                                | $15        |
| BNC Male-to-Male Cable    | DAC CH0 to Amp Input                                  | $8         |
| BNC Breakout Cable        | Amp Monitor Out to ADS1115                            | $14        |
| USB-A to USB-B Cable      | Raspberry Pi to DAC connection                        | $5         |
| Micro-HDMI to HDMI Cable  | Pi to touchscreen video connection                    | $8         |
| Heatsink & Fan            | Cooling solution for Pi 5                             | $10        |

**Total Estimated Cost: ~$414**

---

**Pinout Table**

| Component          | Pi Pin / Port        | Connected To         | Notes                            |
|-------------------|----------------------|----------------------|----------------------------------|
| ADS1115 SDA       | GPIO2 (Pin 3)        | I²C Data             | Feedback ADC line                |
| ADS1115 SCL       | GPIO3 (Pin 5)        | I²C Clock            | Feedback ADC line                |
| ADS1115 VDD       | 3.3V (Pin 1)         | Power Input          |                                  |
| ADS1115 GND       | GND (Pin 6)          | Ground               |                                  |
| ADS1115 A0        | —                    | Amp Monitor Out      | Reads analog feedback signal     |
| Relay IN1         | GPIO18 (Pin 12)      | Relay Control        | Enables/disables relay           |
| Relay VCC         | 5V (Pin 2)           | Power Input          |                                  |
| Relay GND         | GND (Pin 6)          | Ground               |                                  |
| Relay COM         | External 5V Supply   |                      | Relay common terminal            |
| Relay NC          | DAC USB Input        |                      | Disconnects DAC when triggered   |
| E-Stop NC         | GPIO17 (Pin 11)      | Digital In           | Pulls LOW when pressed           |
| E-Stop COM        | GND (Pin 6)          | Ground               |                                  |
| DAC USB-B         | USB 3.0 Port         | Raspberry Pi         | DAC control and power            |
| DAC CH0           | —                    | Amp BNC Input        | ±10 V waveform output            |
| DAC GND           | —                    | Amp GND              | Shared signal reference          |
| Touchscreen HDMI  | Micro-HDMI 0         | Raspberry Pi         | Video output                     |
| Touchscreen USB   | USB-A Port           | Raspberry Pi         | Touch interface                  |
| Power Supply      | USB-C Port           | Raspberry Pi         | Main system power                |

---

**Software Architecture**

Python modules used in the controller:

- `main.py` – Runs core logic, initiates UI and manages waveform output  
- `waveform.py` – Handles sine and sweep waveform generation  
- `dac.py` – Interfaces with MCC DAC using `mcculw`  
- `adc.py` – Reads feedback via ADS1115 over I²C  
- `safety.py` – Monitors GPIO for E-stop trigger  
- `logging.py` – Saves data to CSV, logs FFT and waveform data  
- `gui.py` – PyQt5 GUI for touchscreen control

---

**Dependencies**

- `numpy`, `scipy` – Signal generation and DSP  
- `mcculw` – MCC USB DAC support  
- `RPi.GPIO` – Raspberry Pi GPIO access  
- `matplotlib` – Live graphing and FFT plotting  
- `psutil` – Detecting USB mount states for file export
- `PyQt5` – For touchscreen control

---

**Data Logging**

- Logged data includes:
  - Commanded waveform voltage  
  - Measured acceleration or monitor signal  
  - E-stop or system faults  
  - Frequency-domain FFT  
- Saved as `.csv` files to internal storage or USB on detection  
- Option to export plots as `.png` alongside data  

---

**Safety Notes**

- Hardware E-stop disables output using both GPIO detection and relay cutoff  
- Relay isolates DAC 5V line to immediately cut analog signal on fault  
- E-stop state is polled continuously during operation  

---

**USB Export Support**

- USB drives are automatically detected using `psutil`  
- On test completion, user can select USB target for exporting `.csv` and `.png` results  

---
