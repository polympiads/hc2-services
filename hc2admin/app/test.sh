export TELEMETRY_CONFIG_TYPE=TEST
export CODEFORCES_PRINTER_TOKEN=NONE

python3 -m coverage run --source=. manage.py test
python3 -m coverage report --fail-under=100
python3 -m coverage html