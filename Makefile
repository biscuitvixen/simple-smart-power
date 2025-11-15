.PHONY: deploy deploy-all libs monitor setup list clean-device pull help

PORT ?= /dev/ttyACM0
MOUNT_PATH ?= /run/media/$(USER)/CIRCUITPY

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
	@echo "Deploying code.py..."
	@if [ -d "$(MOUNT_PATH)" ]; then \
		echo "Using mounted filesystem at $(MOUNT_PATH)..."; \
		cp code.py $(MOUNT_PATH)/code.py; \
		sync; \
		echo "✓ Deployment complete"; \
	else \
		echo "ERROR: CIRCUITPY not mounted at $(MOUNT_PATH)"; \
		echo "Please mount the device first or check MOUNT_PATH"; \
		exit 1; \
	fi

deploy-all:
	@echo "Deploying all files..."
	@if [ -d "$(MOUNT_PATH)" ]; then \
		echo "Using mounted filesystem at $(MOUNT_PATH)..."; \
		cp code.py $(MOUNT_PATH)/code.py; \
		if [ -f settings.toml ]; then \
			cp settings.toml $(MOUNT_PATH)/settings.toml; \
		else \
			echo "⚠ settings.toml not found, skipping"; \
		fi; \
		sync; \
		echo "✓ Deployment complete"; \
	else \
		echo "ERROR: CIRCUITPY not mounted at $(MOUNT_PATH)"; \
		echo "Please mount the device first or check MOUNT_PATH"; \
		exit 1; \
	fi

libs:
	@echo "Installing/updating CircuitPython libraries..."
	@circup install --auto --auto-file code.py
	@echo "✓ Libraries updated"

monitor:
	@echo "Opening serial monitor on $(PORT)..."
	@echo "Press Ctrl+A then K to exit screen"
	@screen $(PORT) 115200

list:
	@echo "Listing files on device..."
	@if [ -d "$(MOUNT_PATH)" ]; then \
		ls -lh $(MOUNT_PATH)/; \
	else \
		echo "ERROR: CIRCUITPY not mounted at $(MOUNT_PATH)"; \
		exit 1; \
	fi

pull:
	@echo "Pulling code.py from device..."
	@if [ -d "$(MOUNT_PATH)" ]; then \
		cp $(MOUNT_PATH)/code.py code.py.backup; \
		echo "✓ Saved to code.py.backup"; \
	else \
		echo "ERROR: CIRCUITPY not mounted at $(MOUNT_PATH)"; \
		exit 1; \
	fi

clean-device:
	@echo "Removing code.py from device..."
	@if [ -d "$(MOUNT_PATH)" ]; then \
		rm -f $(MOUNT_PATH)/code.py; \
		sync; \
		echo "✓ code.py removed"; \
	else \
		echo "ERROR: CIRCUITPY not mounted at $(MOUNT_PATH)"; \
		exit 1; \
	fi
