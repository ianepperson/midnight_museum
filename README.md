# Midnight Museum
Code to drive the lights for the Midnight Museum of That One Time at Burningman

## Architecture

The project uses light bulbs and microcontrollers with the ESPHome firmware loaded. The main code connects directly to each bulb and issues commands.

### Threads

There are many I/O bound tasks that run the museum lights. The tasks are run using the Python async/await cooperative threads. Direct references to different handlers are passed to the instantiation to allow control across async threads.

1) Lights Communication Thread - handles sending messages to the Lights via ESPHome.
2) Effects Driver Thread - calculates the light values and transmits them to the MQTT Comms Thread via a queue.
3) Webserver Thread - handles web requests using the [Quart](https://quart.palletsprojects.com/en/latest/index.html) microframework.

## Effects Driver

The effects need to drive the 25 lights in a 5x5 grid and show interesting patterns. To accomplish this, a graphic will be loaded into memory and pixels within
the graphic will be read in the same 5x5 pattern to determine the color of the associated light. At specific intervals (ideally 5 times per second) a new position
within the graphic will be calculated and the light updated - in essence dragging the focus along the image and shifting the lights.

This allows the light patterns to be defined by an image file - if you want waves, make a wavy image and load it!


## Installing

Use [Poetry](https://python-poetry.org/)

Once Poetry is installed, use git to check out the repo, then use

> poetry install

To install all the dependencies.

Run

> poetry shell

to open a shell with the virtual environment is set up. Once in that shell, you can run the application with

> python main.py

### Raspberry Pi


Poetry installer:

- curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

Seems there needs to be a more packages:

 - ffi library (for C extensions)
   - sudo apt-get install libffi-dev
 - Rust compiler (for the crypto library that ESPHome seems to want)
   - curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
 - SSL Library
   - sudo apt-get install libssl-dev
