# Backend

## Run

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build` from the `backend` folder.
3. Apply migrations:
   - `docker compose exec django python manage.py migrate`

## Notes

- Django is exposed on `http://localhost:8000`
- Flower is available on `http://localhost:5555`
