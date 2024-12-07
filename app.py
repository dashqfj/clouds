from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate 
from flask_caching import Cache  # Для кэширования

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройка Redis и кэширования
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = 'redis'  # Имя сервиса Redis из docker-compose
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://redis:6379/0'

# Инициализация объектов
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Инициализация Flask-Migrate
cache = Cache(app)  # Инициализация кэширования с Redis

# Модель User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# CRUD-операции
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@app.route('/users', methods=['GET'])
@cache.cached(timeout=60)  # Кэшируем запросы на 60 секунд
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list)

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    data = request.get_json()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/')
def home():
    return 'Welcome to the home page!'

@app.route('/data')
def data():
    return 'This is some data!'

# Очистка кэша для всех пользователей
@app.route('/clear_cache', methods=['DELETE'])
def clear_cache():
    cache.clear()  # Сбрасываем весь кэш
    return jsonify({'message': 'Cache cleared successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
