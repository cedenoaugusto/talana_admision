# pip install pytest
import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test suite for 'usuarios'
def test_create_user():
    payload = {
        "nombres": "neo",
        "apellidos": "anderson",
        "email": "matrix@talana.cl",
        "estado": "activo"
    }
    response = requests.post(f"{BASE_URL}/users", json=payload)
    assert response.status_code == 201, f"Valor valor esperado 201, se obtuvo {response.status_code}"
    assert "id" in response.json(), "Response body should contain 'id'"

def test_get_all_users():
    response = requests.get(f"{BASE_URL}/users")
    assert response.status_code == 200, f"Valor valor esperado 200, se obtuvo {response.status_code}"
    assert isinstance(response.json(), list), "Response should be a list"

def test_get_user_by_id():
    user_id = 5  # Example user ID
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 200, f"Valor valor esperado 200, se obtuvo {response.status_code}"
    assert response.json().get("id") == user_id, "Returned user ID does not match"

def test_update_user():
    user_id = 5  # Example user ID
    payload = {
        "nombres": "augusto j",
        "apellidos": "cedeño picon",
        "email": "ac5@pm.me",
        "estado": "activo"
    }
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=payload)
    assert response.status_code == 200, f"Valor valor esperado 200, se obtuvo {response.status_code}"
    assert response.json().get("nombres") == "augusto j", "User name not updated"

def test_delete_user():
    user_id = 2  # Example user ID
    payload = {"confirm": True}
    response = requests.delete(f"{BASE_URL}/users/{user_id}", json=payload)
    assert response.status_code == 204, f"Valor valor esperado 204, se obtuvo {response.status_code}"

# Test suite for 'preguntas'
def test_create_question():
    payload = {
        "pregunta": "¿Cuanto es 2 + 2?",
        "dificultad": "facil",
        "puntaje": 1,
        "estado": "activo",
        "categoria": "Matematica",
        "respuestas": [
            {"respuesta": "Uno", "es_correcta": False, "estado": "activo"},
            {"respuesta": "Cuatro", "es_correcta": True, "estado": "activo"}
        ]
    }
    response = requests.post(f"{BASE_URL}/questions", json=payload)
    assert response.status_code == 201, f"Valor valor esperado 201, se obtuvo {response.status_code}"
    assert "id" in response.json(), "Response body should contain 'id'"

def test_get_all_questions():
    response = requests.get(f"{BASE_URL}/questions")
    assert response.status_code == 200, f"Valor valor esperado 200, se obtuvo {response.status_code}"
    assert isinstance(response.json(), list), "Response should be a list"

def test_update_question():
    question_id = 2  # Example question ID
    payload = {
        "id": question_id,
        "pregunta": "¿Cuál es la capital de Chile?",
        "dificultad": "facil",
        "categoria": "Geografia",
        "puntaje": 1,
        "estado": "activo",
        "respuestas": [
            {"id": 22, "respuesta": "Chile", "es_correcta": False, "estado": "activo", "pregunta_id": 4},
            {"id": 23, "respuesta": "Santiago", "es_correcta": False, "estado": "activo", "pregunta_id": 4},
            {"id": 24, "respuesta": "Santiago de Chile", "es_correcta": True, "estado": "activo", "pregunta_id": 4}
        ]
    }
    response = requests.put(f"{BASE_URL}/questions/{question_id}", json=payload)
    assert response.status_code == 200, f"Valor valor esperado 200, se obtuvo {response.status_code}"
    assert response.json().get("pregunta") == "¿Cuál es la capital de Chile?", "Question not updated"

def test_delete_question():
    question_id = 1  # Example question ID
    payload = {"confirm": True}
    response = requests.delete(f"{BASE_URL}/questions/{question_id}", json=payload)
    assert response.status_code == 204, f"Valor valor esperado 204, se obtuvo {response.status_code}"

# More tests can be added for 'trivias', 'trivia/preguntas', and 'trivia/usuarios' as required.

if __name__ == "__main__":
    pytest.main()
