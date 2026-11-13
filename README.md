# CargoHub FastAPI + PostgreSQL prototype

Dit is een lege projectstructuur voor het CargoHub-prototype. Er zijn nog geen endpoints of tabellen.

## Installeren (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Vul vervolgens je eigen PostgreSQL-wachtwoord in `.env` in.

## Verbinding testen

```powershell
python test_connection.py
```

Deze test start geen FastAPI-server en wijzigt geen tabellen.
