
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

def test_get_cards():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("get","/get_cards",
                        headers={"Authorization":f"Bearer {token}"})
    assert card.json()["status_code"] == status.HTTP_200_OK

def test_change_word():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    card = client.request("get","/change_word",
                        params={"word":"","new_word":""},
                        headers={"Authorization":f"Bearer {token}"})

# def test_change_description():
#     pass

def test_delete_word_not_found():
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    delete_words = client.request("delete","/delete_card",
                                    params={"word":"word","description":"description"},
                                    headers={"Authorization":f"Bearer {token}"})
    assert delete_words.json()["detail"]=="word not found"

# @pytest.mark.parametrize("word,description",
#                          [("Apple", "A round fruit that can be red, green, or yellow."),
#                           ("Book", "Something you read."),
#                           ("Cat", "A small animal that people often keep at home."),
#                           ("Dog", "A common animal that people keep as a pet."),
#                           ("Happy", "Feeling good and pleased."),
#                           ("House", "A building where people live."),
#                           ("School", "A place where students learn."),
#                           ("Water", "A clear liquid that people drink."),
#                           ("Friend", "A person you like and know well."),
#                           ("Food", "Things that people eat.")])
# def test_delete_cards(word,description):
#     find_user = client.request("post","/login",
#                                json={"name":"Amir","password":"Amir1234"})
#     token = find_user.json()["token"]
#     delete_words = client.request("delete","/delete_card",
#                                   params={"word":word,"description":description},
#                                   headers={"Authorization":f"Bearer {token}"})
#     assert delete_words.json()["detail"]=="word deleted"