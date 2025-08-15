# src/order_manager/core/engine.py

import logging
from dataclasses import dataclass


@dataclass
class MarketTick:
    time: str
    price: float
    size: float
    side: str


class Engine:
    def __init__(self, strategy, wallet):
        self.strategy = strategy
        self.wallet = wallet
        self.tick_count = 0

    def process_trade(self, trade_info):
        """Process a live trade from the protocol."""
        self.tick_count += 1
        tick = MarketTick(
            time=trade_info["time"],
            price=trade_info["price"],
            size=trade_info["size"],
            side=trade_info["side"],
        )

        logging.debug(f"[Engine] Processing tick {self.tick_count}: {tick}")

        # Ask the strategy if we should place an order
        order = self.strategy.on_tick(self, tick)

        if order:
            logging.info(
                f"[Engine] Strategy wants to {order.side} {order.qty} {order.symbol}"
            )
            self.execute_order(order)

    def execute_order(self, order):
        """In live mode this would send to Solana DEX."""
        logging.info(f"[Engine] EXECUTING ORDER → {order}")
        # TODO: connect to on-chain transaction sender here (will be not implemented yet)
