## Standard Library Differences

**Be aware of differences in Python 3.7 vs. later versions:**

### `dict` preserves insertion order
- Python 3.7+ guarantees dict insertion order
- This is a language feature, not just an implementation detail
- Safe to rely on dict ordering in Python 3.7+

### `asyncio` differences
- Python 3.7 has older asyncio API
- `asyncio.run()` exists but may behave differently than 3.8+
- `asyncio.create_task()` exists in 3.7
- Some asyncio features from 3.8+ are not available

### `dataclasses` available but limited
- `dataclasses` module exists in Python 3.7
- Some features added in 3.8+ (like `frozen=True` on fields) are not available
- Use with caution if targeting strict 3.7.0 compatibility

### String methods
- Most string methods work the same
- Some edge cases may differ from 3.8+