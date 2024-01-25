from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import os
import secrets

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuration Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuration de la clé secrète
app.secret_key = secrets.token_hex(16)

# Configuration des dossiers de médias
app.config['UPLOAD_FOLDER'] = 'app/static/medias'
app.config['THMBS_FOLDER'] = 'app/static/thmbs'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Classe User pour Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def is_authenticated(self):
        return True  # Ajoutez votre logique d'authentification si nécessaire

# Fonction pour vérifier les extensions autorisées
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Fonction de chargement de l'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Générer un nom de fichier unique
def generate_unique_filename(filename):
    random_name = secrets.token_hex(8)  # 8 caractères hexadécimaux, ajustez la longueur selon vos besoins
    _, file_extension = os.path.splitext(filename)
    return f"{random_name}{file_extension}"

# Page protégée par l'authentification
@app.route('/')
@login_required
def protected():
    thmbs_folder = app.config['THMBS_FOLDER']

    # Ajoutez un message d'impression pour vérifier le chemin absolu du répertoire
    abs_thmbs_path = os.path.abspath(thmbs_folder)
    print(f"Chemin absolu du répertoire {thmbs_folder}: {abs_thmbs_path}")

    # Affichez le contenu du répertoire pour le débogage
    print(f"Contenu de {thmbs_folder} : {os.listdir(thmbs_folder)}")

    images = os.listdir(thmbs_folder)
    # Trier les images par date de téléchargement (en utilisant la dernière modification)
    images = sorted(images, key=lambda x: os.path.getmtime(os.path.join(thmbs_folder, x)), reverse=True)
    return render_template('index.html', images=images, user=current_user)


# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Déplacez la génération du mot de passe haché à l'intérieur de cette fonction
    hashed_password = bcrypt.generate_password_hash("votremotdepasse").decode("utf-8")

    if request.method == 'POST':
        password_attempt = request.form['password']
        if bcrypt.check_password_hash(hashed_password, password_attempt):
            user = User(user_id=1)  # Remplacez par la logique pour obtenir l'utilisateur depuis la base de données
            login_user(user)
            return redirect(url_for('protected'))
        else:
            return 'Mot de passe incorrect'
    return render_template('login.html')

# Page de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Téléchargement de fichiers
@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return redirect(request.url)

    files = request.files.getlist('files')

    for file in files:
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        # Générer un nom de fichier unique
        new_filename = generate_unique_filename(file.filename)

        # Enregistrement dans le dossier 'medias' avec le nouveau nom
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        # Enregistrement dans le dossier 'thmbs' avec redimensionnement et le nouveau nom
        thumbnail_path = os.path.join(app.config['THMBS_FOLDER'], f"thumb_{new_filename}")

        # Ouvrir l'image avec Pillow
        original_image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        # Redimensionner l'image à une largeur de 180 pixels
        resized_image = original_image.resize((180, int(original_image.height * (180 / original_image.width))))

        # Enregistrement de l'image redimensionnée
        resized_image.save(thumbnail_path)

    return redirect(url_for('protected'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
