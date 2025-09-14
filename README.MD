# Email Validator API

REST API for validating email addresses, including format, DNS, SPF, DKIM, DMARC, and SMTP checks.

Note: To support large number of email addresses, batch processing can be of great addition to this application which is absent at the moment.

---

## Requirements

- Docker & Docker Compose
- Python 3.11+ (for development outside Docker)

---

## Quick Start (with Docker)

1. **Clone the repository:**
   ```sh
   git clone git@github.com:ln2khanal/email_validator.git
   cd email_validator
   ```

2. **Build and start the services:**
   ```sh
   docker-compose up --build
   ```

3. **The API will be available at:**  
   [http://localhost:8000/](http://localhost:8000/)

---

## API Usage

### Endpoint

`POST /api/validate-emails/`

#### Request Body

```json
{
  "emails": [
    "test@example.com",
    "user@gmail.com"
  ]
}
```

#### Response Example

```json
[
  {
    "email": "test@example.com",
    "valid_format": true,
    "dns_mx": true,
    "spf": "...",
    "dkim": {
      "selector": "default",
      "record": "..."
    },
    "dmarc": "...",
    "smtp_reachable": true,
    "smtp_info": "250 OK",
    "status": "deliverable"
  },
  ...
]
```

---

## Development

1. **Install dependencies (optional, for local dev):**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Django server:**
   ```sh
   python manage.py runserver
   ```

3. **Inspect logs:**
   Application loggings, django.log & error.log can be inspected
   ```
   docker exec -it email_validator_api bash
   cd logs
   tail -f *.log
   ```

---

## Configuration

- **Environment Variables:**
  - `FROM_EMAIL_ADDRESS`: The email address used as the sender for SMTP checks (default: `info@org.local`)
  - `CACHE_HOST`: Hostname for memcached (default: `email_validator_memcached` in Docker)

---

## File Structure

- `docker/` — Dockerfile and entrypoint script
- `validator/` — Django app with API, utils, and validators
- `email_validator_local/` — Django project settings and config

---

## Notes

- For best SMTP results, set `FROM_EMAIL_ADDRESS` to a valid address from your domain.
- The API uses caching for repeated checks to improve performance.
- DKIM selector checks use common defaults; not all domains will have DKIM records.

---

## License

MIT