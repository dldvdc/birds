# Utiliser une image Python officielle
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requis dans le conteneur
COPY requirements.txt .
COPY app/ app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel Flask écoute
EXPOSE 5000

# Définir l'environnement de production
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

# Commande pour démarrer l'application Flask
CMD ["python", "app/app.py"]
