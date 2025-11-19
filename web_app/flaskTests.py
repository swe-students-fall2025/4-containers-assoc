import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from app import create_app, User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = "test_secret"
    with app.test_client() as client:
        yield client

def test_register_post_new_user(client):
    mock_id = ObjectId()
    new_user_data = {"_id": mock_id, "username": "Hermione", "email": "hermione@gmail.com", "password": "secret"}

    def find_one_side_effect(query):
        if query.get("email") == "hermione@gmail.com":
            return None
        if "_id" in query:
            return new_user_data
        return None

    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.side_effect = find_one_side_effect
        mock_db.users.insert_one.return_value.inserted_id = mock_id

        data = {"username": "Hermione", "email": "hermione@gmail.com", "password": "secret"}
        response = client.post('/register', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Hermione" in response.data

def test_register_post_existing_user(client):
    existing_user = {"_id": ObjectId(), "username": "Harry", "email": "harry@gmail.com", "password": "secret"}

    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.return_value = existing_user

        data = {"username": "Harry", "email": "harry@gmail.com", "password": "secret"}
        response = client.post('/register', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Email already registered" in response.data

def test_login_post_success(client):
    user_doc = {"_id": ObjectId(), "email": "harry@gmail.com", "password": "secret"}

    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.return_value = user_doc

        data = {"email": "harry@gmail.com", "password": "secret"}
        response = client.post('/login', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_login_post_wrong_password(client):
    user_doc = {"_id": ObjectId(), "email": "harry@gmail.com", "password": "secret"}

    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.return_value = user_doc

        data = {"email": "harry@gmail.com", "password": "wrong"}
        response = client.post('/login', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Wrong password" in response.data

def test_login_post_unregistered_email(client):
    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.return_value = None

        data = {"email": "unknown@gmail.com", "password": "secret"}
        response = client.post('/login', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b"Email not registered" in response.data

def test_profile_route(client):
    mock_id = ObjectId()
    user_doc = {"_id": mock_id, "username": "Harry", "email": "harry@gmail.com", "password": "secret"}

    with patch.object(client.application, 'db', new=MagicMock()) as mock_db:
        mock_db.users.find_one.return_value = user_doc
        with client.session_transaction() as sess:
            sess['_user_id'] = str(mock_id)

        response = client.get('/profile', follow_redirects=True)
        assert response.status_code == 200
        assert b"Harry" in response.data


def test_spell_view_found(client):
    spell_data = {"spell": "Expelliarmus", "description": "Disarming spell"}
    with patch.object(client.application, 'spells_col', new=MagicMock()) as mock_col:
        mock_col.find_one.return_value = spell_data
        response = client.get('/spells/Expelliarmus')
        assert response.status_code == 200
        assert b"Expelliarmus" in response.data

def test_spell_view_not_found(client):
    with patch.object(client.application, 'spells_col', new=MagicMock()) as mock_col:
        mock_col.find_one.return_value = None
        response = client.get('/spells/UnknownSpell')
        assert response.status_code == 404

def test_api_spells(client):
    spells_list = [{"spell": "Expelliarmus"}, {"spell": "Lumos"}]
    with patch.object(client.application, 'spells_col', new=MagicMock()) as mock_col:
        mock_col.find.return_value = spells_list
        response = client.get('/api/spells')
        assert response.status_code == 200
        assert b"Expelliarmus" in response.data
        assert b"Lumos" in response.data


def test_profile_requires_login(client):
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in" in response.data

def test_spells_view_filters(client):
    spells_list = [{"spell": "Alohomora"}, {"spell": "Expelliarmus"}]
    with patch.object(client.application, 'spells_col', new=MagicMock()) as mock_col:
        mock_col.find.return_value = spells_list
        response = client.get('/?q=Alohomora&t=magic&p=easy')
        assert response.status_code == 200
        assert b"Alohomora" in response.data

def test_register_login_get_pages(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data  

    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data
    
def test_register_post_missing_fields(client):
    response = client.post('/register', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please fill in all fields!" in response.data

def test_login_post_missing_fields(client):
    response = client.post('/login', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please fill in both fields!" in response.data


