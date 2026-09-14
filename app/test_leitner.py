
import pytest
from main import app
from fastapi.testclient import TestClient
from fastapi import status
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
    assert card.json() == "card created"

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

def test_change_word():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("put","/change_word",
                        params={"word":"Apple","new_word":"Egg"},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"]=="word changed"

def test_change_word_word_not_found():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("put","/change_word",
                        params={"word":"Apple","new_word":"Egg"},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"]=="word not found"

def test_change_word_duplicate_name():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("put","/change_word",
                        params={"word":"Egg","new_word":"Egg"},
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"]=="duplicate name"

def test_change_description():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("put","/change_description",
                          params={"word":"Egg","new_description":"An oval object laid by a bird, often eaten"},
                          headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"]=="description changed"

def test_change_description_word_not_found():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("put","/change_description",
                          params={"word":"Apple","new_description":"An oval object laid by a bird, often eaten"},
                          headers={"Authorization":f"Bearer {token}"})
    assert card.json()["detail"]=="word not found"

def test_delete_word_not_found():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    delete_words = client.request("delete","/delete_card",
                                    params={"word":"word","description":"description"},
                                    headers={"Authorization":f"Bearer {token}"})
    assert delete_words.json()["detail"]=="word not found"

@pytest.mark.parametrize("word,description",
                         [("Egg", "A round fruit that can be red, green, or yellow."),
                          ("Book", "Something you read."),
                          ("Cat", "A small animal that people often keep at home."),
                          ("Dog", "A common animal that people keep as a pet."),
                          ("Happy", "Feeling good and pleased."),
                          ("House", "A building where people live."),
                          ("School", "A place where students learn."),
                          ("Water", "A clear liquid that people drink."),
                          ("Friend", "A person you like and know well."),
                          ("Food", "Things that people eat.")])
def test_delete_cards(word,description):
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    delete_words = client.request("delete","/delete_card",
                                  params={"word":word,"description":description},
                                  headers={"Authorization":f"Bearer {token}"})
    assert delete_words.json()["detail"]=="word deleted"