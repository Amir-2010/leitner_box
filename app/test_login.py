
from main import app
from schemas import *
from fastapi.testclient import TestClient
from router_login import create_token
import pytest

client = TestClient(app)

@pytest.mark.parametrize("name,password",
                         [("Amir","Amir1234"),
                          ("Daniel","Daniel1234"),
                          ("Reza","Reza1234"),
                          ("Mary","Mary1234"),
                          ("Billy","Billy1234")])
def test_signup(name,password):
    result = client.request("post","/signup",json={"name":name,"password":password})
    result.json()["detail"]=="user created"
    result = client.request("post","/signup",json={"name":"Amir","password":"Amir"})
    result.json()["detail"]=="duplicate name"

@pytest.mark.parametrize("name,password",
                         [("Amir","Amir1234"),
                          ("Daniel","Daniel1234"),
                          ("Reza","Reza1234"),
                          ("Mary","Mary1234"),
                          ("Billy","Billy1234")])
def test_login(name,password):
    # name not found
    result = client.request("post","/login",json={"name":"Gholi","password":"Gholi"})
    assert result.json()["detail"] == "name not found"
    # wrong password
    result = client.request("post","/login",json={"name":"Amir","password":"Gholi"})
    assert result.json()["detail"] == "wrong password"
    # correct
    result = client.request("post","/login",json={"name":name,"password":password})
    assert result.json()["detail"]=="login successfully"

@pytest.mark.parametrize("name,password,new_name",
                         [("Amir","Amir1234","Amir1234"),
                          ("Daniel","Daniel1234","Daniel1234"),
                          ("Reza","Reza1234","Reza1234"),
                          ("Mary","Mary1234","Mary1234"),
                          ("Billy","Billy1234","Billy1234")])

def test_rename(name,password,new_name):
    # name changed
    result = client.request("post","/login",json={"name":name,"password":password})
    assert result.json()["detail"] == "login successfully"
    token = result.json()["token"]
    rename_result = client.request("put","/rename",
                            params={"new_name":new_name},
                            json={"name":name,"password":password},
                            headers={"Authorization":f"Bearer {token}"})
    assert rename_result.json()["detail"]=="name changed"

def test_rename_duplicate_name():
    # duplicate name
    result = client.request(
        "post", "/login",
        json={"name": "Daniel1234", "password": "Daniel1234"}
    )
    token = result.json()["token"]
    result = client.request("put", "/rename",
                            params={"new_name": "Daniel1234"},
                            json={"name": "Daniel1234", "password": "Daniel1234"},
                            headers={"Authorization": f"Bearer {token}"})
    assert result.json()["detail"] == "duplicate name"

@pytest.mark.parametrize("name,password,new_password",
                         [("Amir1234","Amir1234","1234"),
                          ("Daniel1234","Daniel1234","1234"),
                          ("Reza1234","Reza1234","1234"),
                          ("Mary1234","Mary1234","1234"),
                          ("Billy1234","Billy1234","1234")])
def test_change_password(name,password,new_password):
    # change password
    result = client.request("post","/login",
                            json={"name":name,"password":password})
    token = result.json()["token"]
    result = client.request("put", "/change_password",
                            params={"new_password": new_password},
                            json={"name": name, "password": password},
                            headers={"Authorization": f"Bearer {token}"})
    assert result.json()["detail"] == "password changed"

@pytest.mark.parametrize("name,password",
                         [("Amir1234","1234"),
                          ("Daniel1234","1234"),
                          ("Reza1234","1234"),
                          ("Mary1234","1234"),
                          ("Billy1234","1234")])
def test_change_password_duplicate_password(name,password):
    result = client.request("post","/login",
                            json={"name":name,"password":password})
    token = result.json()["token"]
    result = client.request("put","/change_password",
                            params={"new_password":password},
                            json={"name":name,"password":password},
                            headers={"Authorization":f"Bearer {token}"})
    assert result.json()["detail"] == "password and new password can't be the same"

@pytest.mark.parametrize("name,password",
                         [("Amir1234","1234"),
                          ("Daniel1234","1234"),
                          ("Reza1234","1234"),
                          ("Mary1234","1234"),
                          ("Billy1234","1234")])
def test_delete(name,password):
    login_result = client.request("post","/login",
                                  json={"name":name,"password":password})
    result = client.request("delete","/delete_user",
                            headers={"Authorization":f"Bearer {login_result.json()["token"]}"})
    assert result.json()["detail"] == "user deleted"