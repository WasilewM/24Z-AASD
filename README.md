# 24Z-AASD

## Tests
- `src/main.py` contains examplary scenario of parking spot reservation.  
- `src/examples/modification.py` contains examplary scenario of reservation modification.  
- `src/examples/no_parkingspots_available` contains examplary scenario where 2 requests are sent and only 1 parking spot is available resulting in 1 successful reservation and 1 failure.  

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

