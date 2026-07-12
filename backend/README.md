# Backend

## Run

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build` from the `backend` folder.
3. Apply migrations:
   - `docker compose exec django python manage.py migrate`

## Notes

- Django is exposed on `http://localhost:8000`
- Flower is available on `http://localhost:5555`


## Remarks for production:

### Note on the password validator

AUTH_PASSWORD_VALIDATORS = [] is left empty as in the original settings — signups accept any password ≥ 8  
chars (enforced by the frontend minLength and the User model's set_password hashing, not by Django's       
built-in validators). When you're ready for production, add the standard validators
(UserAttributeSimilarityValidator, MinimumLengthValidator, etc.) in one settings change.

### Note on token storage

Frontend uses localStorage (your chosen dev-friendly option). When you're ready to harden: move to HttpOnly  cookies + a same-origin proxy route, and add the rest_framework_simplejwt.token_blacklist app +
BLACKLIST_AFTER_ROTATION=True so /api/auth/logout/ can actually revoke.

### Note on key management

You need to decrypt and use these keys at runtime when nodes call external APIs — so hashing is out by definition. Fernet + key versioning is the right long-term answer but key rotation is a Phase 4+ concern, not a Phase 0 concern. Build it simple now, the column structure from option 1 doesn't block you from adding a key_version column later when you actually need rotation.

(one line: "generate with python -c 'from cryptography.fernet import Fernet;
     print(Fernet.generate_key().decode())'").
