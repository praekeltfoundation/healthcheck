### Contacts application

This application includes `Contact` and `Case` models, as well as following celery tasks: `send_contact_update` and `perform_nofitications_check`.
API receives cases, registers them and notifies about being in contact.

Example of incoming API request:
```json
{
    "msisdn": "+27820001009",
    "external_id": "qwerty",
    "timestamp": "2020-08-14 17:11:54.131028",
}
```
`msisdn` field is extracted and a `Contact` instance is created from it.
`Case` instance is created from `external_id` and `timestamp` fields. `Contact` is notified about contact by modifing a field in [Turn.io API](https://whatsapp.turn.io/docs/index.html). After contact has expired (contact length is configurable) another notification is sent.