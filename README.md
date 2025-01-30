# rainyday
Made for Hack Club's [Neon](https://neon.hackclub.com) YSWS. A configurable dashboard with a chill, randomly generated rainy background. Hence the name.

## Features
- Ranomly generated rainy background
- 3 foreground modes: Clock, Hackatime, and Pomodoro
- or disable the foreground altogether and enjoy the ambience

## Setup
You'll need an [Adafruit IO](https://io.adafruit.com) account. Paste your username and key into `code.py`, and create a feed called `fg_type`. Then create a dashboard with a keypad and link it up to the `fg_type` field.

You'll need to set up Hackatime in two places: at the start of the script and at the end. Replace the Slack ID with yours and paste in your key.
