#!/usr/bin/python
# 2020 Andrew Villeneuve
# Configure raspberry pi GPIO pins as output-high

from gpiozero import LED

relay01 = LED(17, active_high=False, initial_value=False)
relay02 = LED(27, active_high=False, initial_value=False)
relay03 = LED(22, active_high=False, initial_value=False)
atomicpi = LED(26, active_high=False, initial_value=False)

