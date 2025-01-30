import random
import time
import os
import socket
import ssl

import adafruit_minimqtt.adafruit_minimqtt as MQTT

import board
import random
import displayio
import framebufferio
import rgbmatrix
import datetime
import requests
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import bitmap_label
from displayio import Bitmap

mode = "none"
pomo_start = 0
cycle = 0

# MQTT stuff from https://v.gd/M2kf6V

## DO NOT SHARE

aio_username = "USERNAME"
aio_key = "AIO KEY"

r = requests.get('http://waka.hackclub.com/api/users/U071JHBEJ7R/statusbar/today', headers={'Authorization': 'Basic REPLACE_WITH_KEY'})

data = r.json()["data"]

### Feeds ###

fg_feed = aio_username + "/feeds/fg-type"


# Define callback methods which are called when events occur
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % fg_feed)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(fg_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    global mode
    global pomo_start
    global cycle
    print(topic + ": " + message)
    if topic == fg_feed:
        print("HI")
        if int(message) == 0:
            mode = "none"
        elif int(message) == 1:
            mode = "clock"
        elif int(message) == 2:
            mode = "waka"
        elif int(message) == 3:
            mode = "pomo"
            pomo_start = time.time()
            cycle = 0
            fg_pomo_i.text = "{ WORK }"
        print(mode)

    
# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=aio_username,
    password=aio_key,
    socket_pool=socket,
    is_ssl=True,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()


displayio.release_displays()


spleen8 = bitmap_font.load_font("spleen-5x8.bdf", Bitmap)
spleen12 = bitmap_font.load_font("spleen-6x12.bdf", Bitmap)
spleen16 = bitmap_font.load_font("spleen-8x16.bdf", Bitmap)

# Initialize the display
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=6,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
SCALE = 1
bitmap = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 65535)
palette = displayio.Palette(65535)
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
bg_group = displayio.Group(scale=SCALE)
bg_group.append(tile_grid)
root = displayio.Group()
root.append(bg_group)
display.root_group = root

color_map = {} #hex code : index
def _get_index_for(color):
    index = color_map.get(color, None)
    if index != None:
        return index

    index = len(color_map)
    print(f"DEBUG: Add {hex(color)} to map at {index}")
    palette[index] = color
    color_map[color] = index
    return index

def place(x, y, color):
    """Place a pixel at (x, y) with the given color."""
    if 0 <= x < bitmap.width and 0 <= y < bitmap.height:
        bitmap[x, y] = _get_index_for(color)
        display.auto_refresh = True

def fill(color):
    """Fill the entire display with the given color."""
    for y in range(bitmap.height):
        for x in range(bitmap.width):
            bitmap[x, y] = _get_index_for(color)
    display.auto_refresh = True


fg_group = displayio.Group()
root.append(fg_group)

fg_clock = bitmap_label.Label(
    spleen16,
    color=0xffffff,

    scale=1,
    text="00:00",
    
)

fg_clock.anchor_point = (0.5, 0.66)
fg_clock.anchored_position = (32,16)
fg_group.append(fg_clock)

fg_waka = bitmap_label.Label(
    spleen16,
    color=0xffffff,

    scale=1,
    text="00:00",
    
)

fg_waka.anchor_point = (0.5, 0.66)
fg_waka.anchored_position = (32,16)


fg_pomo = bitmap_label.Label(
    spleen16,
    color=0xffffff,

    scale=1,
    text="00:00",
    
)

fg_pomo.anchor_point = (0.5, 0.66)
fg_pomo.anchored_position = (32,16)

fg_pomo_i = bitmap_label.Label(
    spleen8,
    color=0xffffff,

    scale=1,
    text="{ WORK }",
    
)

fg_pomo_i.anchor_point = (0.5, 0.66)
fg_pomo_i.anchored_position = (32,26)

tick = 0
droplets = []

# Rain stuff
droplet_b = displayio.Bitmap(1,4,5)
droplet_b[0,0] = 1
droplet_b[0,1] = 2
droplet_b[0,2] = 3
droplet_b[0,3] = 4

droplet_p = displayio.Palette(5)
droplet_p[4] = 0x027bfc
droplet_p[3] = 0x015dbf
droplet_p[2] = 0x024082
droplet_p[1] = 0x002449
droplet_p[0] = 0x0





for n in range(0,21):
    droplets.append(displayio.TileGrid(bitmap=droplet_b,pixel_shader=droplet_p,width=1,height=1,tile_width=1,tile_height=4,default_tile=0,x=random.randint(0,64),y=random.randint(0,32)))

for d in droplets:
    bg_group.append(d)

def clear_fg():
    while True:
        if len(fg_group) > 0:
            fg_group.pop()
        else:
            break

def rain():
    for d in droplets:
        d.y+=1
        if d.y>32:
            d.y=-3

def update_clock():
    if not fg_clock in fg_group:
        clear_fg()
        fg_group.append(fg_clock)
            
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-7)))

    fg_clock.text = f"{now.hour:02}:{now.minute:02}"

def update_waka():
    if not fg_waka in fg_group:
        clear_fg()
        fg_group.append(fg_waka)
    fg_waka.text = f'{data["grand_total"]["hours"]:02}:{data["grand_total"]["minutes"]:02}'

def update_none():
    if len(fg_group) > 0:
        clear_fg()

def update_pomo():
    global pomo_start
    global cycle
    if not fg_pomo in fg_group:
        clear_fg()
        fg_group.append(fg_pomo)
        fg_group.append(fg_pomo_i)
    diff = time.time() - pomo_start
    if fg_pomo_i.text == "{ WORK }":
        total = 20 * 60
    if fg_pomo_i.text == "{ BREAK }":
        total = 5 * 60
    if fg_pomo_i.text == "{ CHILL }":
        total = 15 * 60
    remaining = total - diff
    if remaining < 1:
        print("next")
        if fg_pomo_i.text == "{ WORK }":
            cycle += 1
            print(cycle)
            if cycle >= 3:
                print("chill")
                cycle = 0
                fg_pomo_i.text = "{ CHILL }"
            else:
                print("break")
                fg_pomo_i.text = "{ BREAK }"
        elif fg_pomo_i.text == "{ BREAK }":
            fg_pomo_i.text = "{ WORK }"
        elif fg_pomo_i.text == "{ CHILL }":
            fg_pomo_i.text = "{ WORK }"

        pomo_start = time.time()
    fg_pomo.text = f'{int(remaining // 60):02}:{int(remaining - (remaining // 60) * 60):02}'

while True:
    # Poll the message queue
    mqtt_client.loop()
    rain()
    tick+=1
    if tick % 32 == 0:
        r = requests.get('http://waka.hackclub.com/api/users/U071JHBEJ7R/statusbar/today', headers={'Authorization': 'Basic REPLACE_WITH_KEY'})

        data = r.json()["data"]
        for d in droplets:
            if d in bg_group:
                bg_group.remove(d)
        droplets = []
        for n in range(0,21):
            droplets.append(displayio.TileGrid(bitmap=droplet_b,pixel_shader=droplet_p,width=1,height=1,tile_width=1,tile_height=4,default_tile=0,x=random.randint(0,64),y=random.randint(0,32)))
        for d in droplets:
            bg_group.append(d)

    if mode == "clock":
        update_clock()
    elif mode == "waka":
        update_waka()
    elif mode == "pomo":
        update_pomo()
    elif mode == "none":
        update_none()

    display.refresh()



