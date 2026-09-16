
from main import app
from schemas import *
from fastapi.testclient import TestClient
from router_login import create_token
import pytest

client = TestClient(app)

# Test user registration with several different users.
# Parametrization allows the same test to be executed with different credentials.
@pytest.mark.parametrize("name,password",
                         [("Amir","Amir1234"),
                          ("Daniel","Daniel1234"),
                          ("Reza","Reza1234"),
                          ("Mary","Mary1234"),
                          ("Billy","Billy1234")])
def test_signup(name,password):
    # Create a new user using the signup endpoint.
    result = client.request("post","/signup",json={"name":name,"password":password})
    # Check that the user was created successfully.
    result.json()["detail"]=="user created"
    # Try to create another user with an existing name.
    # This should be rejected as a duplicate.
    result = client.request("post","/signup",json={"name":"Amir","password":"Amir"})
    # Check that the API detects the duplicate username.
    result.json()["detail"]=="duplicate name"

# Test login with valid and invalid credentials.
@pytest.mark.parametrize("name,password",
                         [("Amir","Amir1234"),
                          ("Daniel","Daniel1234"),
                          ("Reza","Reza1234"),
                          ("Mary","Mary1234"),
                          ("Billy","Billy1234")])
def test_login(name,password):
    # Test login with a username that does not exist.
    result = client.request("post","/login",json={"name":"Gholi","password":"Gholi"})
    assert result.json()["detail"] == "name not found"
    # Test login with an existing username but an incorrect password.
    result = client.request("post","/login",json={"name":"Amir","password":"Gholi"})
    assert result.json()["detail"] == "wrong password"
    # Test successful login with valid credentials.
    result = client.request("post","/login",json={"name":name,"password":password})
    assert result.json()["detail"]=="login successfully"

# Test changing the username of an authenticated user.
@pytest.mark.parametrize("name,password,new_name",
                         [("Amir","Amir1234","Amir1234"),
                          ("Daniel","Daniel1234","Daniel1234"),
                          ("Reza","Reza1234","Reza1234"),
                          ("Mary","Mary1234","Mary1234"),
                          ("Billy","Billy1234","Billy1234")])
def test_rename(name,password,new_name):
    # Log in first because changing the username requires authentication.
    result = client.request("post","/login",json={"name":name,"password":password})
    assert result.json()["detail"] == "login successfully"
    # Get the authentication token returned by the login endpoint.
    token = result.json()["token"]
    # Send the request to change the username.
    rename_result = client.request("put","/rename",
                            params={"new_name":new_name},
                            json={"name":name,"password":password},
                            headers={"Authorization":f"Bearer {token}"})
    # Verify that the username was changed successfully.
    assert rename_result.json()["detail"]=="name changed"

# Test that a username cannot be changed to an existing username.
def test_rename_duplicate_name():
    # Log in to obtain an authentication token.
    result = client.request(
        "post", "/login",
        json={"name": "Daniel1234", "password": "Daniel1234"}
    )
    token = result.json()["token"]
    # Try to rename the user to a name that is already in use.
    result = client.request("put", "/rename",
                            params={"new_name": "Daniel1234"},
                            json={"name": "Daniel1234", "password": "Daniel1234"},
                            headers={"Authorization": f"Bearer {token}"})
    # Verify that the duplicate-name error is returned.
    assert result.json()["detail"] == "duplicate name"

# Test successfully changing the password for multiple users.
@pytest.mark.parametrize("name,password,new_password",
                         [("Amir1234","Amir1234","1234"),
                          ("Daniel1234","Daniel1234","1234"),
                          ("Reza1234","Reza1234","1234"),
                          ("Mary1234","Mary1234","1234"),
                          ("Billy1234","Billy1234","1234")])
def test_change_password(name,password,new_password):
    # Log in with the current password to get an authentication token.
    result = client.request("post","/login",
                            json={"name":name,"password":password})
    token = result.json()["token"]
    # Send the new password to the password-change endpoint.
    result = client.request("put", "/change_password",
                            params={"new_password": new_password},
                            json={"name": name, "password": password},
                            headers={"Authorization": f"Bearer {token}"})
    # Verify that the password was changed successfully.
    assert result.json()["detail"] == "password changed"

# Test that the new password cannot be identical to the current password.
@pytest.mark.parametrize("name,password",
                         [("Amir1234","1234"),
                          ("Daniel1234","1234"),
                          ("Reza1234","1234"),
                          ("Mary1234","1234"),
                          ("Billy1234","1234")])
def test_change_password_duplicate_password(name,password):
    # Log in using the user's current password.
    result = client.request("post","/login",
                            json={"name":name,"password":password})
    token = result.json()["token"]
    # Try to change the password to the same password.
    result = client.request("put","/change_password",
                            params={"new_password":password},
                            json={"name":name,"password":password},
                            headers={"Authorization":f"Bearer {token}"})
    # Verify that the API rejects the unchanged password.
    assert result.json()["detail"] == "password and new password can't be the same"

# Test deleting users after the account operations are complete.
@pytest.mark.parametrize("name,password",
                         [("Amir1234","1234"),
                          ("Daniel1234","1234"),
                          ("Reza1234","1234"),
                          ("Mary1234","1234"),
                          ("Billy1234","1234")])
def test_delete(name,password):
    # Log in to obtain the authentication token required for deleting the account.
    login_result = client.request("post","/login",
                                  json={"name":name,"password":password})
    # Delete the authenticated user's account.
    result = client.request("delete","/delete_user",
                            headers={"Authorization":f"Bearer {login_result.json()["token"]}"})
    # Verify that the user was successfully deleted.
    assert result.json()["detail"] == "user deleted"