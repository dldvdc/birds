# Utiliser une image Nginx officielle
FROM nginx:latest

# Supprimer la configuration par défaut de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copier le fichier de configuration personnalisé
COPY nginx.conf /etc/nginx/conf.d/
