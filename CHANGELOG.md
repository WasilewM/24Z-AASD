# Changelog

Format according to the [keepachangelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.2.5] - 2025.01.02

## Fixed

- User ends while no offers for requested time.

## [0.2.4] - 2024.12.18

## Fixed

- Parking offer selection if none is available.

## Added

- Example with no available parking spot.
- Example with mutliple requests.

## [0.2.3] - 2024.12.17

## Fixed

- Reservations UUID generation to be unique.

## [0.2.2] - 2024.12.16

### Added

- Coordinator_id in User's Reservation.

## [0.2.1] - 2024.12.16

### Changed

- Models use pydantic.

## [0.2.0] - 2024.12.14

### Added

- Modifying reservation in Parking Agent.
- Improved logging.

### Fixed

- Message receivers in all agents.
- Message encoding and decoding.
- Reservation modification logic in User.

### Changed

- Dockerfile with sleep infinity command to not exit the container but allow to run different scripts.

## [0.1.5] - 2024.12.10

### Added

- Option to check parking spots from `time_start` to `time_stop`.
- Option to make a parking spot reservation.
- Dumb modification requests handling - random answers `True` or `False`.

### Changed

- `ParkingAgent._available_parking_spots` is a list now - it represents next 24 hours of parking spots availability.

## [0.1.4] - 2024-12-04

### Added

- `User` agent with main methods for creating and modifying a reservation.

### Changed

- `reservation_id` attribute to `ReservationResponse` message.

## [0.1.3] - 2024-12-01

### Changed

- We have to make assumption that every location is covered with RegionalCoordinator.

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
  message_body=ClassName(**json.loads(message.body))
  ```
