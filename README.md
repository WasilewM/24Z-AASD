# 24Z-AASD

## Tests
- `src/main.py` contains examplary scenario of parking spot reservation.  
- `src/examples/modification.py` contains examplary scenario of reservation modification.  
- `src/examples/no_parkingspots_available` contains examplary scenario where 2 requests are sent and only 1 parking spot is available resulting in 1 successful reservation and 1 failure.  

In order to run tests:  
1. Set up the environemnt: `docker build -t spade_hello:0.2.5 . && docker compose up -d`. Use the lastest image version from the `CHANGELOG.md`.  
2. Exec into the `aasd-spade_main-1` container.  
3. Go to the directory containing examples: `cd src/examples`.  
4. Run chosen test, e.g.: `python3 modification.py` and observe logs.  

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

