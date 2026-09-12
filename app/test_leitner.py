
import pytest
from main import app
from fastapi.testclient import TestClient
from router_leitner import *

client = TestClient(app)

@pytest.mark.parametrize("word,description",
                         [("Apple", "A round fruit that can be red, green, or yellow."),
                          ("Book", "Something you read."),
                          ("Cat", "A small animal that people often keep at home."),
                          ("Dog", "A common animal that people keep as a pet."),
                          ("Happy", "Feeling good and pleased."),
                          ("House", "A building where people live."),
                          ("School", "A place where students learn."),
                          ("Water", "A clear liquid that people drink."),
                          ("Friend", "A person you like and know well."),
                          ("Food", "Things that people eat.")])
def test_create_card(word,description):
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("post","/create_card",
                        params={"word":word,"description":description},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"] == "card created"

@pytest.mark.parametrize("word,description",
                         [("Apple", "A round fruit that can be red, green, or yellow."),
                          ("Book", "Something you read."),
                          ("Cat", "A small animal that people often keep at home."),
                          ("Dog", "A common animal that people keep as a pet."),
                          ("Happy", "Feeling good and pleased."),
                          ("House", "A building where people live."),
                          ("School", "A place where students learn."),
                          ("Water", "A clear liquid that people drink."),
                          ("Friend", "A person you like and know well."),
                          ("Food", "Things that people eat.")])
def test_create_card_duplicate_card(word,description):
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("post","/create_card",
                        params={"word":word,"description":description},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"] == "duplicate card name"

@pytest.mark.parametrize("word,description",
                         [("Apple", "A round fruit that can be red, green, or yellow."),
                          ("Book", "Something you read."),
                          ("Cat", "A small animal that people often keep at home."),
                          ("Dog", "A common animal that people keep as a pet."),
                          ("Happy", "Feeling good and pleased."),
                          ("House", "A building where people live."),
                          ("School", "A place where students learn."),
                          ("Water", "A clear liquid that people drink."),
                          ("Friend", "A person you like and know well."),
                          ("Food", "Things that people eat.")])
def test_get_cards(word,description):
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("post","/create_card",
                        params={"word":word,"description":description},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"] == "duplicate card name"

# def test_change_word():
#     pass

# def test_change_description():
#     pass

# def delete_cards():
#     pass