.PHONY: deploy deploy-all libs monitor setup list clean-device pull help

PORT ?= /dev/ttyACM0

help:
	@echo "CircuitPython Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup        - Initialize project (copy settings.toml.example)"
	@echo "  deploy       - Deploy code.py to device"
	@echo "  deploy-all   - Deploy code.py and settings.toml to device"
	@echo "  libs         - Install/update CircuitPython libraries with circup"
	@echo "  monitor      - Open serial monitor (screen)"
	@echo "  list         - List files on device"
	@echo "  pull         - Pull code.py from device"
	@echo "  clean-device - Remove code.py from device"
	@echo ""
	@echo "Usage: make <target> [PORT=/dev/ttyACM0]"
	@echo "Example: make deploy PORT=/dev/ttyUSB0"

setup:
	@echo "Setting up development environment..."
	@if [ ! -f settings.toml ]; then \
		cp settings.toml.example settings.toml; \
		echo "✓ Created settings.toml - please edit with your credentials"; \
	else \
		echo "✓ settings.toml already exists"; \
	fi

deploy:
	@echo "Deploying code.py to $(PORT)..."
	@ampy --port $(PORT) put code.py
	@echo "✓ Deployment complete"

deploy-all:
	@echo "Deploying all files to $(PORT)..."
	@ampy --port $(PORT) put code.py
	@if [ -f settings.toml ]; then \
		ampy --port $(PORT) put settings.toml; \
	else \
		echo "⚠ settings.toml not found, skipping"; \
	fi
	@echo "✓ Deployment complete"

libs:
	@echo "Installing/updating CircuitPython libraries..."
	@circup install --auto --auto-file code.py
	@echo "✓ Libraries updated"

monitor:
	@echo "Opening serial monitor on $(PORT)..."
	@echo "Press Ctrl+A then K to exit screen"
	@screen $(PORT) 115200

list:
	@echo "Listing files on device at $(PORT)..."
	@ampy --port $(PORT) ls

pull:
	@echo "Pulling code.py from device..."
	@ampy --port $(PORT) get code.py > code.py.backup
	@echo "✓ Saved to code.py.backup"

clean-device:
	@echo "Removing code.py from device..."
	@ampy --port $(PORT) rm code.py
	@echo "✓ code.py removed"
