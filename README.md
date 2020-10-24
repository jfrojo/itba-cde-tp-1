# itba-cdi-tp-1
ETL built for Cloud Data Architect - module 1 at ITBA.

Data set source: https://data.world/chandrasekar/consumer-complaints

Build db and etl images:

docker-compose up

To run the etl, just start the previously built image in a new docker container.

Sample queries images:

docker build .

Again to run the queries just run the previously built image in a new docker container.

Note: In order for the queries container to be able to connect to the docker compose's database, the option '--network etl-network' must be added.


Business:

The dataset contains all the complains that have been reported by the consumers over several products of different companies over time, and the company's response, among other pertinent stuff.