"""RescueNet automatic installer.

Usage:
	py setup.py

Before running this script, install manually:
  - Python 3.11+         https://www.python.org/downloads/
      During install check "Add Python to PATH", then restart terminal.
  - PostgreSQL 16/17/18  https://www.postgresql.org/download/windows/
      Remember the password you set for user 'postgres'.

The PostgreSQL service starts automatically after installation by default.

After installation the app is available at:
  http://127.0.0.1:8000/        main app
  http://127.0.0.1:8000/admin/  admin panel (login: admin / admin)

This script:
  1. creates/keeps a local virtual environment
  2. installs dependencies
  3. writes a local .env file with database credentials
  4. creates the PostgreSQL database if psql is available
  5. runs migrations
  6. creates a demo superuser
  7. optionally seeds demo data
  8. optionally starts the development server
"""

from __future__ import annotations

import getpass
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"
ENV_FILE = PROJECT_DIR / ".env"

DEFAULT_DB_NAME = "rescuenet"
DEFAULT_DB_USER = "postgres"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "5432"
DEFAULT_SUPERUSER_NAME = "admin"
DEFAULT_SUPERUSER_EMAIL = "admin@example.com"
DEFAULT_SUPERUSER_PASSWORD = "admin"


def info(message: str) -> None:
	print(message, flush=True)


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
	info(f"  > {' '.join(cmd)}")
	completed = subprocess.run(cmd, cwd=PROJECT_DIR, env=env)
	if completed.returncode != 0:
		raise SystemExit(f"[ERROR] Command failed: {' '.join(cmd)}")


def run_capture(cmd: list[str], *, env: dict[str, str] | None = None) -> str:
	completed = subprocess.run(cmd, cwd=PROJECT_DIR, env=env, capture_output=True, text=True)
	if completed.returncode != 0:
		raise SystemExit(completed.stderr.strip() or completed.stdout.strip() or f"Command failed: {' '.join(cmd)}")
	return completed.stdout.strip()


def venv_python() -> Path:
	return VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "python"


def python_launcher() -> list[str]:
	if sys.platform == "win32" and shutil.which("py"):
		return ["py", "-3"]
	if shutil.which("python3"):
		return ["python3"]
	if shutil.which("python"):
		return ["python"]
	raise SystemExit("No Python launcher found. Install Python 3.11+ first.")


def ensure_venv() -> None:
	if venv_python().exists():
		info("[1/8] Virtual environment already exists.")
		return

	info("[1/8] Creating virtual environment...")
	run(python_launcher() + ["-m", "venv", str(VENV_DIR)])


def create_env_file(db_password: str, superuser_password: str) -> dict[str, str]:
	info("[2/8] Writing local .env file...")
	env_values = {
		"DATABASE_NAME": input(f"  Database name [{DEFAULT_DB_NAME}]: ").strip() or DEFAULT_DB_NAME,
		"DATABASE_USER": input(f"  Database user [{DEFAULT_DB_USER}]: ").strip() or DEFAULT_DB_USER,
		"DATABASE_PASSWORD": db_password,
		"DATABASE_HOST": input(f"  Database host [{DEFAULT_DB_HOST}]: ").strip() or DEFAULT_DB_HOST,
		"DATABASE_PORT": input(f"  Database port [{DEFAULT_DB_PORT}]: ").strip() or DEFAULT_DB_PORT,
		"DJANGO_SECRET_KEY": os.urandom(24).hex(),
		"RESCUENET_SUPERUSER_NAME": DEFAULT_SUPERUSER_NAME,
		"RESCUENET_SUPERUSER_EMAIL": DEFAULT_SUPERUSER_EMAIL,
		"RESCUENET_SUPERUSER_PASSWORD": superuser_password,
	}

	with ENV_FILE.open("w", encoding="utf-8", newline="\n") as handle:
		for key, value in env_values.items():
			handle.write(f"{key}={value}\n")

	info(f"  Wrote {ENV_FILE.name}")
	return env_values


def install_requirements(python: Path) -> None:
	info("[3/8] Installing Python dependencies...")
	run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
	run([str(python), "-m", "pip", "install", "-r", "requirements.txt"])


def find_psql() -> str | None:
	if shutil.which("psql"):
		return "psql"

	if sys.platform == "win32":
		for version in ("18", "17", "16"):
			candidate = Path(rf"C:\Program Files\PostgreSQL\{version}\bin\psql.exe")
			if candidate.exists():
				return str(candidate)

	return None


def ensure_database(env_values: dict[str, str], db_password: str) -> None:
	info("[4/8] Checking PostgreSQL database...")
	psql = find_psql()
	if psql is None:
		info("  [WARN] psql not found - skipping database auto-create.")
		return

	env = os.environ.copy()
	env["PGPASSWORD"] = db_password

	db_name = env_values["DATABASE_NAME"]
	db_user = env_values["DATABASE_USER"]
	db_host = env_values["DATABASE_HOST"]
	db_port = env_values["DATABASE_PORT"]

	exists = run_capture([
		psql,
		"-h", db_host,
		"-p", db_port,
		"-U", db_user,
		"-d", "postgres",
		"-tAc", f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';",
	], env=env)

	if exists.strip() == "1":
		info(f"  Database '{db_name}' already exists.")
		return

	run([
		psql,
		"-h", db_host,
		"-p", db_port,
		"-U", db_user,
		"-d", "postgres",
		"-c", f"CREATE DATABASE {db_name};",
	], env=env)
	info(f"  Database '{db_name}' created.")


def migrate(python: Path, env_values: dict[str, str]) -> None:
	info("[5/8] Running migrations...")
	env = os.environ.copy()
	env.update(env_values)
	env["DJANGO_SETTINGS_MODULE"] = "core.settings"
	run([str(python), "manage.py", "migrate"], env=env)


def ensure_superuser(python: Path, env_values: dict[str, str]) -> None:
	info("[6/8] Ensuring demo superuser exists...")
	env = os.environ.copy()
	env.update(env_values)
	env["DJANGO_SETTINGS_MODULE"] = "core.settings"

	script = r'''
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("RESCUENET_SUPERUSER_NAME", "admin")
email = os.environ.get("RESCUENET_SUPERUSER_EMAIL", "admin@example.com")
password = os.environ.get("RESCUENET_SUPERUSER_PASSWORD", "admin")

user = User.objects.filter(username=username).first()
if user is None:
	user = User.objects.create_superuser(username=username, email=email, password=password)
else:
	user.email = email
	user.is_staff = True
	user.is_superuser = True
	user.role = "admin"
	if password:
		user.set_password(password)
	user.save()

print(f"Superuser ready: {username}")
'''.strip()

	run([str(python), "-c", script], env=env)


def maybe_seed(python: Path, env_values: dict[str, str]) -> None:
	answer = input("[7/8] Seed demo data? [Y/n]: ").strip().lower()
	if answer == "n":
		info("  Skipping seed step.")
		return

	admins = input("  Superusers [3]: ").strip() or "3"
	dispatchers = input("  Dispatchers [50]: ").strip() or "50"
	rescuers = input("  Rescuers [50]: ").strip() or "50"
	resources = input("  Resources [60]: ").strip() or "60"
	incidents = input("  Incidents [200]: ").strip() or "200"

	env = os.environ.copy()
	env.update(env_values)
	env["DJANGO_SETTINGS_MODULE"] = "core.settings"
	run([
		str(python),
		"manage.py",
		"seed_database",
		"--admins", admins,
		"--dysp", dispatchers,
		"--rescuers", rescuers,
		"--resources", resources,
		"--incidents", incidents,
	], env=env)


def maybe_runserver(python: Path, env_values: dict[str, str]) -> None:
	answer = input("[8/8] Start development server now? [Y/n]: ").strip().lower()
	if answer == "n":
		info("Done.")
		return

	env = os.environ.copy()
	env.update(env_values)
	env["DJANGO_SETTINGS_MODULE"] = "core.settings"
	run([str(python), "manage.py", "runserver"], env=env)


def main() -> None:
	print("=" * 60)
	print("  RescueNet automatic install")
	print("=" * 60)
	print("  Tip: Press enter when asked to input a value to use the default value written in the [parenthesis].")
	print()

	ensure_venv()
	python = venv_python()

	db_password = getpass.getpass(f"Database password for '{DEFAULT_DB_USER}': ")
	superuser_password = getpass.getpass(f"Demo superuser password [{DEFAULT_SUPERUSER_PASSWORD}]: ").strip() or DEFAULT_SUPERUSER_PASSWORD

	env_values = create_env_file(db_password, superuser_password)
	install_requirements(python)
	ensure_database(env_values, db_password)
	migrate(python, env_values)
	ensure_superuser(python, env_values)
	maybe_seed(python, env_values)
	maybe_runserver(python, env_values)


if __name__ == "__main__":
	main()

