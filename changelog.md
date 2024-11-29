### 28-11

Przygotowano strukturę projektu, podzielono aktorów na oddzielne pliki. Założenie - lokalizacja x,y w liczbach całkowitych (nie bawmy się w geo), proponuję tworzyć body message jako dataclass w katalogu src/messages. Ładować za pomocą: `message_body=NazwaKlasy(**json.loads(message.body))`.

 `action` w metadanych wiadomości pozwala określić do jakiego zachowania koordynatora ma trafić message.

 Agenty Userów muszą wysyłać check-parking-offers do wszystkich dostępnych koordynatorów, koordynator, który obsługuje dany region odpowie, pozostali nie.

### 29-11

Interakcje z dokumentacji o nazwach ProcessReservation oraz SendResponse miały podwójne akty komunikacyjne np. refuse | agree. Z racji na obsługę odpowiedzi przez jedno zachowanie zmieniono performatywę na inform, ponieważ nie można dawać dwóch jednocześnie.
