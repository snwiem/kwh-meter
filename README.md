# kwh-meter

# Description

A simple web application to track the used energy power of our house. The idea is to be able to note down selectivly the current value of the central energy power meter. The value can be tracked at any time of a day.

# Requirements (concept phase)

The app must be implemented mobile first. the basic idea is to track the values using a phone device, so the ui must be mobile compatible and easy to use.

There currently is no requirements for authentication, authorization and multi tenency. The following domain objects are identified until now

- one single engergy power meter with the follwing meta data
  - Zählernummer (ID)
  - Address (Street, Housenumber, Postal Code and City)
- each tracked value must contain at least
  - Date and time the value was picked (not necessarily but usually by default the same time the value is entered)
  - The value itself
  - An optional comment field

The app must provide the following statistical data calculations

- absolute Energy used between certain time range (from, to, until now, since)
- comparision of daily usage of several days (maybe line-diagram 0:00-24:00 with possibility to overlay selected days)

But this is early phase as the collection of data points is not not fixed to specific points in time.

# MVP

The minimum target of the MVP is

- open UI using a browser (desktop and mobile, latter preferred)
- create the energy power meter we want to collect data for. exactly one meter is required for MVP
- enter the current power usage value for the selected power meter
- list all entered records
- export all entered records (as json or csv/tsv) -> export from web should be done as download

