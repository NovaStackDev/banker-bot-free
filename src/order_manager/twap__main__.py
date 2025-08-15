import argparse
import logging
from .utils.helpers import setup_logging, load_yaml, get_nested
from .core.engine import Engine, Wallet, MockAMM
from .strategies.twap import TWAPStrategy

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/settings.yaml")
    args = ap.parse_args()

    setup_logging(logging.INFO)
    cfg = load_yaml(args.config)

    symbol = get_nested(cfg, "app", "symbol", default="ASSET")
    ticks = int(get_nested(cfg, "app", "ticks", default=20))

    w = Wallet(
        quote_usd=float(get_nested(cfg, "wallet", "quote_usd", default=1000.0)),
        positions=dict(get_nested(cfg, "wallet", "positions", default={}) or {}),
    )

    venue = MockAMM(
        base_reserves=float(get_nested(cfg, "venue", "reserves_base", default=100000.0)),
        quote_reserves=float(get_nested(cfg, "venue", "reserves_quote", default=1000000.0)),
        fee_bps=int(get_nested(cfg, "venue", "fee_bps", default=30)),
    )

    risk_max_pos = float(get_nested(cfg, "risk", "max_position", default=10.0))
    risk_max_notional = float(get_nested(cfg, "risk", "max_order_notional", default=200.0))
    risk_slip_cap = int(get_nested(cfg, "risk", "max_slippage_bps", default=100))

    eng = Engine(symbol, w, venue, risk_max_pos, risk_max_notional, risk_slip_cap)

    strat_name = str(get_nested(cfg, "strategy", "name", default="twap")).lower()
    params = get_nested(cfg, "strategy", "params", default={}) or {}

    if strat_name == "twap":
        strat = TWAPStrategy(
            symbol=symbol,
            side=str(params.get("side", "buy")),
            total_qty=float(params.get("total_qty", 5.0)),
            slices=int(params.get("slices", 5)),
            max_slippage_bps=risk_slip_cap,
        )
    else:
        raise SystemExit(f"Unknown strategy: {strat_name}")

    start_nav = eng.mark_to_market()
    for _ in range(ticks):
        order = strat.on_tick(eng)
        if order:
            eng.execute(order.side, order.qty, order.max_slippage_bps)
    end_nav = eng.mark_to_market()

    print(f"Start NAV: {start_nav:.4f} USD")
    print(f"End   NAV: {end_nav:.4f} USD")
    print(f"Quote Balance: {eng.wallet.quote_usd:.4f} USD")
    print(f"Base Position: {eng.wallet.pos(symbol):.6f} {symbol}")
    print(f"Fees Paid: {eng.wallet.fees_paid:.4f} USD-equivalent")

if __name__ == "__main__":
    main()
