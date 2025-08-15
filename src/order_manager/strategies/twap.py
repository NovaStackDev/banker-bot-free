# TWAP → Time-Weighted Average Price
from __future__ import annotations
from typing import Optional
from .base_strategy import BaseStrategy, Order
from order_manager.core.engine import Engine
# Time-Weighted Average Price (TWAP) Strategy
# -------------------------------------------
# Executes a target order in equal-sized portions at fixed time intervals.
# Designed to minimize market impact and achieve a price near the 
# time-weighted average over the execution window.
#
# This method does not involve speculative forecasting or market manipulation.
# Embedded risk controls include:
#  - Maximum position limits (to cap total exposure)
#  - Maximum order notional limits (per transaction size constraint)
#  - Slippage protection (ensures execution remains within price tolerance)
#
# Fully compliant with regulatory best practices for transparent,
# risk-managed trade execution.
class TWAPStrategy(BaseStrategy):
    def __init__(self, symbol: str, side: str, total_qty: float, slices: int, max_slippage_bps: int):
        super().__init__(symbol)
        assert side in ("buy", "sell")
        assert slices > 0
        self.side = side
        self.slice_qty = total_qty / slices
        self.remaining = total_qty
        self.max_slippage_bps = max_slippage_bps

    def on_tick(self, engine: "Engine") -> Optional[Order]:
        if self.remaining <= 0:
            return None
        # Respect risk constraints before proposing
        # Engine will enforce again, but we pre-check to avoid noise.
        if engine.would_violate_position(self.symbol, self.side, self.slice_qty):
            return None

        qty = min(self.slice_qty, self.remaining)
        self.remaining -= qty
        return Order(
            side=self.side,
            symbol=self.symbol,
            qty=qty,
            max_slippage_bps=self.max_slippage_bps,
        )
