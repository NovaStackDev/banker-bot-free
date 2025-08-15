import asyncio
import logging
from core.omprotocol import TradingProtocol
from order_manager.utils.helpers import setup_logging

def main():
    setup_logging(logging.INFO)
    protocol = TradingProtocol(config_path="config/settings.yaml")
    asyncio.run(protocol.run())

if __name__ == "__main__":
    main()
