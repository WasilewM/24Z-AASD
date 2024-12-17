# 24Z-AASD

## Tests
- `src/main.py` contains examplary scenario of parking spot reservation.  
- `src/examples/example_modification.py` contains examplary scenario of reservation modification

## FIPA

| Interaction             | Communication act FIPA  | Communication flow                            |
|-------------------------|-------------------------|-----------------------------------------------|
| SendParkingRequest      | `query-ref`             | UserAgent -> RegionalCoordinatorAgent         |
| CheckParkingOffers      | `query-ref`             | RegionalCoordinatorAgent -> Agenty parkingowe |
| SendParkingAvailability | `inform`                | ParkingAgent -> RegionalCoordinatorAgent      |
| ConsolidateOffers       | `inform`                | RegionalCoordinatorAgent -> UserAgent         |
| ModifyReservation       | `request`               | UserAgent -> RegionalCoordinatorAgent         |
| SendReservationRequest  | `request`               | UserAgent -> RegionalCoordinatorAgent         |
| ProcessReservation      | `refuse \| agree`       | ParkingAgent -> RegionalCoordinatorAgent      |
| SendResponse            | `confirm \| disconfirm` | RegionalCoordinatorAgent -> UserAgent         |

