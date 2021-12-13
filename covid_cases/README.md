# COVID Cases

The goal of this app is to scrape various sources on a schedule, and store that data in the database. It can then serve that data on an API for applications to consume, most notably the CASES keyword on ContactNDoH.

## Syncing business logic

Each row of data has a date field, this is the date that the data is for, and it is assumed that the data is updated daily. If it is updated more often than daily, then we will overwrite and keep the last value for the day. The data is sourced from 3 sources:

### NICD GIS API
This gives us the number of cases down to the ward level, also segregated by age and gender. The main importance of this data for us is to be able to provide case numbers at a province level. These are stored in the WardCase model.

### SACoronaVirus homepage
The homepage has counters on it at the bottom. These counters give us useful totals for cases, vaccinations, recoveries, and deaths. We also get number of tests administered. This is stored in the SACoronavirusCounter model.

### SACoronaVirus daily cases images
These images are useful in that we attach it to the message reply we give to the user, so they get the information in text form as well as image form. We also download and save these images in our storage, to ensure that we can still serve images if the upstream service is down, similar to how we can still serve the text information if any of the upstream services are down. This is stored in the SACoronavirusCaseImage model.

## Summary business logic
For the summary endpoint, /v2/covidcases/contactndoh, there is some business logic to determine what the latest numbers are from the data in the database.

For the daily image, and the counters on the homepage, we just service the latest that we have in the database.

For the timestamp, we take that from the last update of the WardCase data. This is a tricky one, since the sources could all be updated at different times, but we're only showing one timestamp to the user.

For the "latest" count, we first try to use the counters on the homepage. We look for the latest counter, and then see if there's a counter for the day before that. If there is, then the different is the latest count. Otherwise we go to the WardCase data, where we do a similar thing: we look at the latest date that we have data for, see if there's data for a day before that, and if there is then the difference is the latest count. If there isn't, then we fall back to the "latest" field in the data. The reason we prioritise looking at the total difference first before looking at the latest field, is that the latest field isn't always correct.

For the latest province counts, we do something similar: we look at the WardCase data, for the latest day and the previous day. If that doesn't exist we fallback to the "latest" field. We also remove the blank and "Pending" provinces from the results.