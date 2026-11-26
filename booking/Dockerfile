# image officielle légère
FROM python:3.13-alpine

WORKDIR /app

# les dépendances d'abord : cette couche reste en cache tant que requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# puis le code et les données
COPY . .

# les données modifiées par le service sont conservées dans un volume
VOLUME ["/app/data"]

EXPOSE 3003

# -u : les print s'affichent directement dans les logs
CMD ["python", "-u", "booking.py"]
