
import pytest
from main import app
from fastapi.testclient import TestClient
from router_leitner import get_db
from router_leitner import *
client = TestClient(app)

# Test creating a new card for an authenticated user.
# Parametrize is used to test the endpoint with multiple words and descriptions.
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
    # Log in first because creating a card requires authentication.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    # Get the JWT token returned by the login endpoint.
    token = find_user.json()["token"]
    # Send the word and description to the create-card endpoint.
    card = client.request("post","/create_card",
                          params={"word":word,"description":description},
                          headers={"Authorization":f"Bearer {token}"})
    # The endpoint should confirm that the card was created.
    assert card.json() == "card created"

# Test that the API prevents creating two cards with the same word.
# The cards created in the previous test are used as duplicate data.
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
    # Authenticate the user before attempting to create another card.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Try to create a card that already exists.
    card = client.request("post","/create_card",
                          params={"word":word,"description":description},
                          headers={"Authorization":f"Bearer {token}"})
    # The API should reject the request because the card name already exists.
    assert card.json()["detail"] == "duplicate card name"

# Test successfully changing the word of an existing card.
def test_change_word():
    # Log in and obtain an authentication token.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Change the card word from Apple to Egg.
    card = client.request("put","/change_word",
                          params={"word":"Apple","new_word":"Egg"},
                          headers={"Authorization":f"Bearer {token}"})
    # Verify that the word was changed successfully.
    assert card.json()["detail"]=="word changed"

# Test the error returned when trying to change a word that cannot be found.
def test_change_word_word_not_found():
    # Authenticate the user before accessing the protected endpoint.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Try to change a word that is expected to no longer exist.
    card = client.request("put","/change_word",
                          params={"word":"Apple","new_word":"Egg"},
                          headers={"Authorization":f"Bearer {token}"})
    # The API should report that the original word was not found.
    assert card.json()["detail"]=="word not found"

# Test that changing a word to an already existing name is rejected.
def test_change_word_duplicate_name():
    # Authenticate the user.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Try to rename Egg to a name that is already being used.
    card = client.request("put","/change_word",
                          params={"word":"Egg","new_word":"Egg"},
                          headers={"Authorization":f"Bearer {token}"})
    # Verify that the duplicate-name error is returned.
    assert card.json()["detail"]=="duplicate name"

# Test successfully updating the description of a card.
def test_change_description():
    # Log in to get permission to modify the card.
    find_user = client.request("post","/login",
                              json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Update the description belonging to the Egg card.
    card = client.request("put","/change_description",
                          params={"word":"Egg","new_description":"An oval object laid by a bird, often eaten"},
                          headers={"Authorization":f"Bearer {token}"})
    # Verify that the description was updated.
    assert card.json()["detail"]=="description changed"

# Test updating a description when the requested card does not exist.
def test_change_description_word_not_found():
    # Authenticate the user.
    find_user = client.request("post","/login",
                              json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Try to update the description of a non-existing card.
    card = client.request("put","/change_description",
                          params={"word":"Apple","new_description":"An oval object laid by a bird, often eaten"},
                          headers={"Authorization":f"Bearer {token}"})
    # The API should return a word-not-found error.
    assert card.json()["detail"]=="word not found"

# Test deleting a card that does not exist.
def test_delete_word_not_found():
    # Authenticate before attempting to delete a card.
    find_user = client.request("post","/login",
                              json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Send an invalid word and description to the delete endpoint.
    delete_words = client.request("delete","/delete_card",
                                  params={"word":"word","description":"description"},
                                  headers={"Authorization":f"Bearer {token}"})
    # Verify that the API correctly reports that the card was not found.
    assert delete_words.json()["detail"]=="word not found"

# Test changing the Leitner box of a card that does not exist.
def test_change_box_card_not_found():
    # Authenticate the user before accessing the protected endpoint.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Use an invalid card ID to test the not-found case.
    answer_word = client.request("put","/change_box",
                                 params={"card_id":55,"correct":True},
                                 headers={"Authorization":f"Bearer {token}"})

    # Verify that the API returns the expected error.
    assert answer_word.json()["detail"]=="card not found"

# Test moving multiple cards through the Leitner box system.
# Each card is tested with a correct answer.
@pytest.mark.parametrize("card_id,status",

                         [(1,True),
                          (2,True),
                          (3,True),
                          (4,True),
                          (5,True),
                          (6,True),
                          (7,True),
                          (8,True),
                          (9,True),
                          (10,True)])
def test_change_box(card_id,status):
    # Log in to obtain authorization for changing the card box.
    find_user=client.request("post","/login",json={"name":"Amir","password":"Amir1234"})
    token=find_user.json()["token"]
    # Send the card ID and whether the user's answer was correct.
    answer_word=client.request("put","/change_box",params={"card_id":card_id,"correct":status},headers={"Authorization":f"Bearer {token}"})
    # A successful box change should return HTTP 200.
    assert answer_word.status_code==200

# Test deleting all cards after the other card operations are completed.
# Parametrization allows the same deletion test to run for every card.
@pytest.mark.parametrize("word,description",
                         [("Egg", "An oval object laid by a bird, often eaten"),
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
    # Authenticate the user before deleting the card.
    find_user = client.request("post","/login",
                               json={"name":"Amir","password":"Amir1234"})
    token = find_user.json()["token"]
    # Delete the card using its word and description.
    delete_words = client.request("delete","/delete_card",
                                  params={"word":word,"description":description},
                                  headers={"Authorization":f"Bearer {token}"})
    # Verify that the card was successfully deleted.
    assert delete_words.json()["detail"]=="word deleted"