Feature: Send request for parking offers

  Rule: The client will only receive any offer if there is any parking near chosen location

  Scenario: There is parking near chosen location
    Given ParkingAgent x=1, y=1, parking_spots=100
    And RegionalCoordinator with x_from=0, x_to=10, y_from=0, y_to=10
    When User1 asks for parking around x=5, y5
    Then User1 receives a list with 1 offers

  Scenario: There are multiple parkings near chosen location
    Given ParkingAgent x=1, y=1, parking_spots=100
    And ParkingAgent x=5, y=6, parking_spots=50
    And ParkingAgent x=10, y=1, parking_spots=15
    And RegionalCoordinator with x_from=0, x_to=10, y_from=0, y_to=10
    When User1 asks for parking around x=5, y5
    Then User1 receives a list with 3 offers

  Scenario: There isn't any parking near chosen location
    Given  RegionalCoordinator with x_from=0, x_to=10, y_from=0, y_to=10
    When User1 asks for parking around x=5, y5
    Then User1 receives a list with 0 offers