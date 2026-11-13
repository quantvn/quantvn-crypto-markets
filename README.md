# QuantVN Crypto Markets

Dữ liệu, backtest và paper trading crypto (Binance spot và hợp đồng vĩnh cửu USD-M) với thư viện **QuantVN**.

Mọi chức năng nằm trong gói `quantvn` trên PyPI. Repo này chứa hướng dẫn, ví dụ chạy được và kiểm thử cho thị trường crypto. Thị trường Việt Nam: [quantvn-vn-markets](https://github.com/quantvn/quantvn-vn-markets) · Thị trường Mỹ: [quantvn-us-markets](https://github.com/quantvn/quantvn-us-markets).

*English: crypto market data, backtests and paper trading with `pip install quantvn` (0.3.0 or later). The examples below run as they are; comments in the code are in English.*

## Cài đặt

```bash
pip install "quantvn>=0.3.0"
```

Không cần API key để lấy dữ liệu. Có key (lấy ở mục Hồ sơ & API Keys trên quantvn.com) thì hạn mức cao hơn:

```python
import quantvn
quantvn.client(apikey="your-apikey")
```

## Dữ liệu

| Bộ dữ liệu | Nội dung | Nguồn | Cập nhật |
|---|---|---|---|
| spot | ~40 cặp USDT của Binance có khối lượng lớn nhất, nến 1 phút từ ngày niêm yết | Kho lưu trữ chính thức của Binance (data.binance.vision, kiểm tra checksum) và REST API của Binance | 10 phút |
| perp | Hợp đồng vĩnh cửu USD-M của các cặp đó, giá khớp cuối | như trên | 10 phút |
| funding | Funding rate từng kỳ (8 giờ, một số mã 4 hoặc 1 giờ), kèm giá mark | Binance | 10 phút |

Nến được gắn nhãn theo **giờ mở cửa**, chỉ gồm nến đã đóng. Khung `1m 5m 15m 30m 1h 4h 1d` lấy từ API dữ liệu QuantVN; các khung khác, mã chưa có trong kho, hoặc khi API không trả lời thì thư viện tải thẳng từ Binance.

```python
from quantvn.crypto.data import get_crypto_hist, get_funding_rates, list_crypto_symbols

list_crypto_symbols("spot")            # các cặp spot trong kho; "perp", "funding"
btc = get_crypto_hist("BTCUSDT", "1h", start="2026-01-01", end="2026-11-01", tz=None)   # UTC
eth = get_crypto_hist("ETHUSDT", "1m", start="2026-11-10", market="perp")               # giờ Việt Nam
fund = get_funding_rates("BTCUSDT", start="2026-10-01")    # Datetime, rate, mark_price
```

| Tham số | Ý nghĩa |
|---|---|
| `interval` | `1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M` |
| `start`, `end` | ngày, giờ hoặc epoch ms; `end` không tính; không có múi giờ thì hiểu là UTC. Không truyền cả hai: giai đoạn 2019-07 đến 2022-12 như bản 0.2 |
| `market` | `"spot"` hoặc `"perp"` |
| `tz` | múi giờ của cột `Datetime` (mặc định giờ Việt Nam; `None` là UTC) |
| `source` | `"auto"` (QuantVN, dự phòng Binance), `"quantvn"`, `"binance"` |

Kết quả: `Datetime, Date, time, Open, High, Low, Close, volume`.

## Paper trading

`quantvn.paper.simulate` tính kết quả đúng như dịch vụ Track Record của QuantVN:

- vị thế quyết định tại giá đóng cửa của một nến được khớp tại giá **mở cửa** của nến sau;
- vị thế là tỷ trọng vốn, vốn bắt đầu từ 1 và cộng dồn;
- phí mỗi chiều: spot (`CRYPTO`) 10 bp, vị thế 0 đến 1; vĩnh cửu (`CRYPTO_PERP`) 5 bp, vị thế -1 đến 1;
- **funding** (vĩnh cửu): kỳ funding tại thời điểm t được tính ở nến đầu tiên mở cửa từ t trở đi, trên tỷ trọng đang giữ trước lệnh khớp ở nến đó: vốn nhân với `1 - tỷ trọng x rate`. Vị thế mua trả khi rate dương, vị thế bán nhận.

```python
from quantvn import paper
from quantvn.crypto.data import get_crypto_hist, get_funding_rates

df = get_crypto_hist("ETHUSDT", "15m", start="2026-09-01", end="2026-11-01", market="perp", tz=None)
df["position"] = ...          # -1..1
fund = get_funding_rates("ETHUSDT", start="2026-09-01", end="2026-11-01")
print(paper.simulate(df, market="CRYPTO_PERP", funding=fund))
```

Kết quả của `simulate` trùng với engine của Track Record: chênh lệch tương đối của NAV dưới 2e-14 trên 200 kịch bản ngẫu nhiên.

Gửi vị thế thật lên Track Record (https://paper.quantvn.com): dịch vụ ghi lại **thời điểm nhận** vị thế và tự định giá bằng dữ liệu Binance của mình; không gửi giá. Xem `examples/04_track_record.py`. `TrackRecord(...).assets()` cho biết thị trường nào đang nhận vị thế: spot đang mở; vĩnh cửu mở sau khi engine có funding được triển khai.

## Ví dụ

| File | Nội dung |
|---|---|
| `examples/01_data.py` | danh sách mã, nến spot và vĩnh cửu, funding |
| `examples/02_paper_perp.py` | chiến lược MA trên ETH vĩnh cửu, có và không có funding |
| `examples/03_backtest_spot.py` | `Backtest_Crypto` và `paper.simulate` trên SOL spot |
| `examples/04_track_record.py` | gửi vị thế lên Track Record (cần email và API key) |

```bash
pip install "quantvn>=0.3.0"
python examples/01_data.py
```

## Hạn mức API

| | Yêu cầu/phút | Dòng/ngày |
|---|---|---|
| Không có key | 30 | 5 triệu |
| Có key | 120 | 50 triệu |

Tối đa 600.000 dòng mỗi yêu cầu (một năm nến 1 phút); thư viện tự chia khoảng thời gian dài và tự chờ khi gặp HTTP 429. Ngoài ra cổng vào giới hạn 5 yêu cầu/giây cho mỗi địa chỉ. `quantvn.marketdata.datasets()` cho biết độ phủ và hạn mức hiện tại.

## Kiểm thử

```bash
pip install "quantvn>=0.3.0" pytest
pytest -q                 # gọi API thật với khoảng thời gian ngắn
```

## Miễn trách nhiệm

Phục vụ nghiên cứu và học tập. Dữ liệu có thể thiếu hoặc sai; kết quả quá khứ không đảm bảo tương lai. Giấy phép MIT.
