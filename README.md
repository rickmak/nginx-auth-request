# Traefik Auth Request Demo

This project demonstrates how to use Traefik's routing (dynamic) configuration to authenticate requests based on HTTP headers.

## Architecture

The setup consists of two services:

1. **Auth**: A Flask service that validates the `x-pretest` header.
2. **Traefik**: Acts as a gateway and reverse proxy, using routing (dynamic) configuration to validate incoming requests.

## How it works

1. The client sends requests to Traefik with or without the `x-pretest` header
2. Traefik forwards the authentication headers to the auth service
3. The auth service checks if the `x-pretest` header contains a valid token
4. If authentication succeeds, Traefik processes the request; otherwise, it returns a 401 error

## Valid Authentication

A valid request must include the header: `x-pretest: valid-token`

## Running the Demo

```bash
docker compose up --build
```

## Traefik Visualization

To verify routers, services, and middlewares for debugging, visit: `http://localhost:8081/dashboard/` after docker containers spin up successfully.

## Testing

Assuming you have configured a virtual environment with Pytest, you can run the unit tests with `pytest -v`.

Or you can test manually:

```bash
# Valid request
curl -v -H "x-pretest: valid-token" http://localhost:8080/health
curl -v -H "x-pretest: valid-token" http://localhost:8080/404

# Invalid request
curl -v -H "x-pretest: wrong-token" http://localhost:8080/health

# Missing header
curl http://localhost:8080
```
