import RPi.GPIO as GPIO

# Only E-stop pin is used
KILL_PIN = 17
kill_callback = None

def setup_gpio(kill_cb):
    global kill_callback
    kill_callback = kill_cb

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(KILL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(KILL_PIN, GPIO.FALLING, callback=handle_kill, bouncetime=200)

def handle_kill(channel):
    if kill_callback:
        kill_callback()

def cleanup_gpio():
    GPIO.cleanup()