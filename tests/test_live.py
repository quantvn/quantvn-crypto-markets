"""Checks against the live QuantVN market-data API and Binance: short windows only."""
import numpy as np
import pandas as pd
import pytest

from quantvn import marketdata, paper
from quantvn.crypto.data import get_crypto_hist, get_funding_rates, list_crypto_symbols


def test_api_is_reachable():
    d = marketdata.datasets()
    names = {x["dataset"] for x in d["datasets"]}
    assert {"crypto_spot", "crypto_perp", "crypto_funding"} <= names


def test_symbols():
    spot = list_crypto_symbols("spot")
    assert "BTCUSDT" in spot and "ETHUSDT" in spot


def test_one_day_of_minutes_is_complete_and_ordered():
    df = get_crypto_hist("BTCUSDT", "1m", start="2026-10-15", end="2026-10-16", tz=None)
    assert len(df) == 1440
    assert df["Datetime"].iloc[0] == pd.Timestamp("2026-10-15", tz="UTC")
    assert df["Datetime"].is_monotonic_increasing
    assert (df["High"] >= df[["Open", "Close"]].max(axis=1)).all()
    assert (df["Low"] <= df[["Open", "Close"]].min(axis=1)).all()


def test_quantvn_and_binance_give_the_same_bars():
    a = get_crypto_hist("ETHUSDT", "1h", start="2026-10-01", end="2026-10-03", tz=None, source="quantvn")
    b = get_crypto_hist("ETHUSDT", "1h", start="2026-10-01", end="2026-10-03", tz=None, source="binance")
    assert len(a) == len(b) == 48
    for c in ("Open", "High", "Low", "Close"):
        np.testing.assert_allclose(a[c].to_numpy(), b[c].to_numpy(), rtol=1e-12)


def test_funding_every_eight_hours():
    f = get_funding_rates("BTCUSDT", start="2026-10-01", end="2026-10-08")
    assert len(f) == 21
    assert (f["Datetime"].diff().dropna() == pd.Timedelta(hours=8)).all()
    assert f["rate"].abs().max() < 0.01


def test_perp_paper_trade_runs_with_funding():
    df = get_crypto_hist("BTCUSDT", "1h", start="2026-10-01", end="2026-10-08", market="perp", tz=None)
    df["position"] = 1.0
    f = get_funding_rates("BTCUSDT", start="2026-10-01", end="2026-10-08")
    r = paper.simulate(df, market="CRYPTO_PERP", funding=f)
    # held long the whole time: funding paid = sum of the rates after the first fill
    after = f[f["Datetime"] > df["Datetime"].iloc[1]]
    assert r.stats["funding"] == pytest.approx(after["rate"].sum(), rel=1e-9)
