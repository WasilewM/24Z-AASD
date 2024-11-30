# Changelog
Format according to the [keepachangelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.2] - 2024-11-30
### Removed
- `hello` agent development directory.

## [0.1.1] - 2024-11-29
### Changed
- `ProcessReservation` and `SendResponse` interactions had duplicate communicative acts like `refuse` | `agree`. Changed the performative to `inform` to handle responses with a single behavior, as multiple performatives cannot be given simultaneously.

## [0.1.0] - 2024-11-28
### Added
- Prepared project structure, separated actors into individual files.
- Set assumption for x, y locations as integers (no geo-based calculations).
- Proposed using `dataclass` for message bodies in `src/messages`, loaded with:
  ```python
  message_body=NazwaKlasy(**json.loads(message.body))

