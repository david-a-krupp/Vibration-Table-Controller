# safety.py
import RPi.GPIO as GPIO

E_STOP_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(E_STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_emergency():
    return GPIO.input(E_STOP_PIN) == GPIO.LOW
