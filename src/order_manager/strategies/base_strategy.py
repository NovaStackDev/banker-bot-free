# src/order_manager/strategies/base_strategy.py
from __future__ import annotations
from typing import Optional
from dataclasses import dataclass

@dataclass
class Order:
    side: str            # "buy" | "sell"
    symbol: str
    qty: float           # base units
    max_slippage_bps: int

class BaseStrategy:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def on_tick(self, engine) -> Optional[Order]:
        raise NotImplementedError
