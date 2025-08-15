# src/order_manager/utils/layouts.py

import struct
from collections import namedtuple

# ===== Serum v3 Event Queue =====

# Serum constants
EVENT_SIZE = 88  # each event in bytes
HEADER_SIZE = 32  # header before events

SerumEvent = namedtuple("SerumEvent", ["side", "price", "size"])

def decode_serum_event_queue(data: bytes, base_decimals: int, quote_decimals: int):
    """
    Parses the Serum EventQueue account binary layout.
    Returns a list of dicts with trade details.
    """
    events = []

    # First 8 bytes => header (seq, head, count, etc.)
    # Serum docs: https://projectserum.com/docs/dex/markets
    head = struct.unpack_from("<Q", data, 8)[0]
    count = struct.unpack_from("<Q", data, 16)[0]

    # Serum event queue is circular
    for i in range(count):
        idx = (head + i) % (len(data) // EVENT_SIZE)
        offset = HEADER_SIZE + idx * EVENT_SIZE
        event_bytes = data[offset: offset + EVENT_SIZE]

        if len(event_bytes) < EVENT_SIZE:
            continue

        # Event layout: https://github.com/project-serum/serum-dex/blob/master/dex/src/state.rs
        event_flags = event_bytes[0]
        side = "buy" if event_flags & 0x80 else "sell"

        # Prices & quantities are in lot sizes
        price_lots = struct.unpack_from("<Q", event_bytes, 8)[0]
        qty_lots = struct.unpack_from("<Q", event_bytes, 16)[0]

        # Convert to human units (this requires market.lot_size info — simplified here)
        # NOTE: In production, you'd fetch lot size + tick size from market account.
        price = price_lots / (10 ** quote_decimals)
        size = qty_lots / (10 ** base_decimals)

        if price > 0 and size > 0:
            events.append({"side": side, "price": price, "size": size})

    return events


# ===== Raydium AMM State =====

def decode_raydium_trade(data: bytes, base_decimals: int, quote_decimals: int):
    """
    Decodes Raydium AMM state account to estimate last swap price.
    This is an approximation: price = quote_reserve / base_reserve.
    """
    # Offsets from Raydium source: https://github.com/raydium-io/raydium-contract-instructions
    base_reserve = struct.unpack_from("<Q", data, 72)[0]
    quote_reserve = struct.unpack_from("<Q", data, 80)[0]

    if base_reserve == 0:
        return {"side": "buy", "price": 0, "size": 0}

    price = (quote_reserve / (10 ** quote_decimals)) / (base_reserve / (10 ** base_decimals))

    # Side guess: If reserves of base increased, someone sold base (buy for AMM)
    side = "buy"  # placeholder — proper way is to diff old vs new reserves

    # Size estimation — we can’t get exact trade size from single snapshot without diff
    size = 0.0

    return {"side": side, "price": price, "size": size}
