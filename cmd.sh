#!/bin/sh
python promptgen.py --generations 10 --fix_weights 1 --lora_cap 2 --crush 1.3 json/default-scene.json >log
