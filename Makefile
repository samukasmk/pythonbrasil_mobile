PYTHON = python
# needs kivy installed or in PYTHONPATH

.PHONY: theming apk clean

theming:
	$(PYTHON) -m kivy.atlas appconf/data/default 1024 tools/theming/*.png
apk:
	buildozer android debug
apk_release:
	buildozer android release
dev:
        OFFLINE_MODE=1 python3.6 app/main.py -m screen:droid2,portrait -m inspector
