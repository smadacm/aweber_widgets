# AWeber Widget RESTer
## Prerequisites
- Docker must be installed
- docker-compose must be installed
- docker-compose should be in $PATH

## Setup and Running
1. clone the repository
2. in a shell, cd to the repository root
3. run `docker-compose up`

This will create and launch the entire stack, which consists of an app container and a "tester" container.
The app container will
- install prerequisite packages from pip (which is non-destructive, so it can run every time the container boots),
- run `flake8`
- generate a random secret for Django
- run schema migrations
- launch the test server

The tester container will
- install prerequisite packages from apk (which is non-destructive, so it can run every time the container boots, but it's slow, so it doesn't),
- pause until the app server responds
- run a series of tests that either output nothing or fail
- print "Tester done. No errors found." to indicate the script finished without encountering problems.

## Endpoints
All endpoints that expect a body use the JSON format with 2 fields:
- `name` is the name of the widget
- `parts_count` is the number of parts

_Example:_ ```{"name": "Widget Name", "parts_count: 5}```

All endpoints return a JSON object with 3 fields:
- `error_number` is an int indicating what the error is _(see below)_
- `error_message` is a string explaining what the error is
- `widgets` is a list of Widget objects returned by the call

The `Widget` object has 5 fields:
- `id` _(int, immutable)_
- `name` _(string, mutable)_
- `parts_count` _(int, mutable)_
- `created_at` _(datetime as string, immutable)_
- `updated_at` _(datetime as string, immutable by user, changes automatically)_

### GET `/widgets/`
List all widgets
- no body expected

### PUT `/widgets/`
Creates a widget
- body expected

### GET `/widgets/<widget_id>/`
Gets the widget with id `<widget_id>`
- no body expected

### PATCH `/widgets/<widget_id>/`
Updates the widget with id `<widget_id>`
- body expected

### DELETE `/widgets/<widget_id>/`
Deletes the widget with id `<widget_id>`
- no body expected

## Possible Errors
- `ERR_A_OK` _(`error_number` 0, HTTP status 200)_ means everything is fine
- `ERR_MODEL_DOES_NOT_EXIST` _(`error_number` 1, HTTP status 404)_ means the requested object does not exist
- `ERR_INVALID_DATA` _(`error_number` 2, HTTP status 400)_ means the provided data was not valid
- `ERR_MALFORMED_DATA` _(`error_number` 3, HTTP status 400)_ means the program was unable to parse the supplied data
