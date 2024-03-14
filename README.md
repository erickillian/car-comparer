# Simple Django Car Comparison Web Application

I created this web app as I wanted an easy tool to compare different car options.

This project was inspired as I myself needed a car and found sites like Kelley Blue Book and Edmunds could have improved functionality for people wanting to compare cars.  (Notibly 5 year cost of ownership was missing from many cars, also would like the option to look at 6, 7, 8, or whatever year cost of ownership easily and specifically compare expenses)

To start I am just working on the backend and trying to connect as many open source datasets into one database so a better app can be built around the datasets.

## Data Sources

- https://vpic.nhtsa.dot.gov/api/
- https://www.fueleconomy.gov/feg/ws/


## Project Setup

First install docker and docker compose on the system.  To test correct installation run 
```sh
docker --version
docker compose version
```

To start project run
```sh
docker compose up --build
```

After project finishes building run
```sh
docker compose exec web python3 manage.py makemigrations
docker compose exec web python3 manage.py migrate
```



## Commands I am using to populate site with API data

The command scrapes all manufacturers from the year 2023 - 2024 using fueleconomy and populates the database with the results.
```sh
docker compose exec web python3 manage.py scrape_fueleconomy --scrape-type manufacturers --start-year 2023 --end-year 2024
```

The command scrapes all vehicle models for various manufacturers for the years 2023 - 2024 using nhtsa and populates the database with the results.
```sh
docker compose exec web python3 manage.py scrape_nhtsa --scrape-type models --start-year 2023 --end-year 2024
```

Populates Vehicle Types using nhtsa data
```sh
docker compose exec web python3 manage.py scrape_nhtsa --scrape-type vehicle_types --start-year 2023 --end-year 2024
```

Populates vehicle variations using fueleconomy database results
```sh
docker compose exec web python3 manage.py scrape_fueleconomy --scrape-type variations --start-year 2023 --end-year 2024
```

## Current Limitations

The biggest limitation of this project seems to be access to public data.  Most data seems to cost money to access apis, and most free datasources are not complete or recent.


## TODO:

- [ ] Look into adding more information to manufacturers using public wikipedia data
- [ ] Determine source of where vehicle sales information can be obtained legally (ideally free)
- [ ] Determine better data source for vehicle variations (current public data source is missing lots of 2024 car data)
- [ ] Add automation scripts to docker image so publically available api data is periodically refreshed
- [ ] Create API views for data so that a front end can be build around the data


