# atoywebapi

atoywebapi is a simple toy RESTful web API server written in Python with fastapi and sqlmodel.

The API does CRUD for facilities-level clean energy investments. The service is backed by a Postgresql database.

This is a toy. Don't use any of this in production.


## Examples

You can interact with the server through various HTTP requests, once the server and database are deployed and running.

From a terminal shell, for example:

```shell

SERVER_URL="http://localhost:8080"

# Posts a facility
curl --location --request POST "${SERVER_URL}/facilities/" \
--header 'Content-Type: application/json' \
--data-raw '{
  "uid": "M.B.6K_TN.0",
  "segment": "Manufacturing",
  "company": "6K Energy",
  "technology": "Batteries",
  "subcategory": "EAM",
  "investment_status": "U",
  "latitude": 35.606,
  "longitude": -88.83,
  "estimated_investment": 200438887,
  "announcement_date": "2023-04-18"
}'

# Get what we just posted
curl --location --request GET "${SERVER_URL}/facilities/M.B.6K_TN.0"

# Post another facility
curl --location --request POST "${SERVER_URL}/facilities/" \
--header 'Content-Type: application/json' \
--data-raw '{
  "uid": "M.B.ABB_VA.0",
  "segment": "Manufacturing",
  "company": "ABB Group",
  "technology": "Batteries",
  "subcategory": "Modules",
  "investment_status": "O",
  "latitude": 37.63792,
  "longitude": -77.39912,
  "estimated_investment": 6013167,
  "announcement_date": "2023-06-19"
}'

# What if you try to post something that already exists?
curl --location --request POST "${SERVER_URL}/facilities/" \
--header 'Content-Type: application/json' \
--data-raw '{
  "uid": "M.B.ABB_VA.0",
  "segment": "Manufacturing",
  "company": "ABB Group",
  "technology": "Batteries",
  "subcategory": "Modules",
  "investment_status": "O",
  "latitude": 37.63792,
  "longitude": -77.39912,
  "estimated_investment": 6013167,
  "announcement_date": "2029-06-19"
}'
# This ^ should get a 409 status code and details on the error.

# Get list of all facilities posted.
curl --location --request GET "${SERVER_URL}/facilities/"

# Get list of all facilities posted with segment of "Manufacturing".
curl --location --request GET "${SERVER_URL}/facilities/?segment=Manufacturing"

# Get list of all facilities posted with segment of "Bacon".
curl --location --request GET "${SERVER_URL}/facilities/?segment=Bacon"

# Get list of all facilities posted with announcement dates before and after a range.
curl --location --request GET "${SERVER_URL}/facilities/?announced_after=2023-01-01&announced_before=2023-06-01"

# Another example of getting a list of all facilities posted with announcement dates before and after a range.
curl --location --request GET "${SERVER_URL}/facilities/?announced_after=2023-06-01&announced_before=2024-12-25"

# Test limit option with pagination
curl --location --request GET "${SERVER_URL}/facilities/?segment=Manufacturing&limit=1"

# Test limit option with pagination, get the second page. Should be different from first page.
curl --location --request GET "${SERVER_URL}/facilities/?segment=Manufacturing&limit=1&offset=1"

# Delete a facility
curl --location --request DELETE "${SERVER_URL}/facilities/M.B.6K_TN.0"
# It should no longer exist here...
curl --location --request GET "${SERVER_URL}/facilities/M.B.6K_TN.0"
```

You can also view GET requests from the comfort of your browser. For example:
http://localhost:8080/facilities/?segment=Manufacturing&announced_after=2023-12-23&limit=1000

See Swagger/OpenAPI documentation at http://localhost:8080/docs


## Getting things running

You can run the server and database locally with Docker Compose:

```
docker compose up
```

gets everything up. And you can interact with the server as described above in [Examples](#examples).

To tear things down, run

```
docker compose down
```

This also removes data stored in the backing database.

## Support
Source code is available online at https://github.com/brews/atoywebapi/. This software is Open Source and available under the Apache License, Version 2.0.

Please file bugs in the [bug tracker](https://github.com/brews/atoywebapi/issues).
