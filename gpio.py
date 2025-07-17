import RPi.GPIO as GPIO

# Pin Definitions
START_PIN = 23
STOP_PIN = 27
KILL_PIN = 17

start_callback = None
stop_callback = None
kill_callback = None

def setup_gpio(start_cb, stop_cb, kill_cb):
    global start_callback, stop_callback, kill_callback
    start_callback = start_cb
    stop_callback = stop_cb
    kill_callback = kill_cb

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(START_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KILL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(START_PIN, GPIO.FALLING, callback=handle_start, bouncetime=200)
    GPIO.add_event_detect(STOP_PIN, GPIO.FALLING, callback=handle_stop, bouncetime=200)
    GPIO.add_event_detect(KILL_PIN, GPIO.FALLING, callback=handle_kill, bouncetime=200)

def handle_start(channel):
    if start_callback:
        start_callback()

def handle_stop(channel):
    if stop_callback:
        stop_callback()

def handle_kill(channel):
    if kill_callback:
        kill_callback()

def cleanup_gpio():
    GPIO.cleanup()