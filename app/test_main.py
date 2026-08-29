
from main import app
from schemas import *
from fastapi.testclient import TestClient
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

def test_rename():
    # name not found
    result = client.request("put","/rename",json={"name":"Gholi","password":"Amir1234","new_name":"Goli"})
    assert result.json()["detail"]=="name not found"
    # wrong password
    result = client.request("put","/rename",json={"name":"Amir","password":"Amir","new_name":"Goli"})
    assert result.json()["detail"]=="wrong password"
    # correct
    result = client.request("put","/rename",json={"name":"Amir","password":"Amir1234","new_name":"Goli"})
    assert result.json()["detail"]=="name changed"
    result = client.request("put","/rename",json={"name":"Goli","password":"Amir1234","new_name":"Amir"})
    assert result.json()["detail"]=="name changed"

def test_change_password():
    # name not found
    result = client.request("put","/change_password",json={"name":"Gholi","password":"Gholi","new_password":"Goli1"})
    assert result.json()["detail"]=="name not found"
    # wrong password
    result = client.request("put","/change_password",json={"name":"Amir","password":"Gholi","new_password":"Gholi1"})
    assert result.json()["detail"]=="wrong password"
    # same input
    result = client.request("put","/change_password",json={"name":"Amir","password":"Amir1234","new_password":"Amir1234"})
    assert result.json()["detail"]=="password and new password can't be the same"
    # correct
    result = client.request("put","/change_password",json={"name":"Amir","password":"Amir1234","new_password":"Amir"})
    assert result.json()["detail"]=="password changed"
    result = client.request("put","/change_password",json={"name":"Amir","password":"Amir","new_password":"Amir1234"})
    assert result.json()["detail"]=="password changed"

@pytest.mark.parametrize("name,password",
                         [("Amir","Amir1234"),
                          ("Daniel","Daniel1234"),
                          ("Reza","Reza1234"),
                          ("Mary","Mary1234"),
                          ("Billy","Billy1234")])
def test_delete(name,password):
    # name not found
    result = client.request("delete","/delete_user",json={"name":"Gholi","password":"Gholi"})
    assert result.json()["detail"] == "name not found"
    # wrong password
    result = client.request("delete","/delete_user",json={"name":name,"password":"Gholi"})
    assert result.json()["detail"] == "wrong password"
    # correct
    result = client.request("delete","/delete_user",json={"name":name,"password":password})
    assert result.json()["detail"] == "user deleted"