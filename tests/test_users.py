from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models


## Test Create User Validation Error
@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


## Test Create User Duplicate Email
@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


## Test Create User Success
@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "image_path" in data
    assert "password" not in data
    assert "password_hash" not in data


## Test Upload Profile Picture
@pytest.mark.anyio
async def test_upload_profile_picture(client: AsyncClient, mocked_aws):
    user = await create_test_user(client)
    token = await login_user(client)

    test_image_path = Path(__file__).parent / "test_image.jpg"
    image_bytes = test_image_path.read_bytes()

    response = await client.patch(
        f"/api/users/{user['id']}/picture",
        files={
            "file": ("profile.jpg", BytesIO(image_bytes), "image/jpeg")
        },  # Sending files as a tuple tells HTTPx to send this data as a multi part upload, what we would expect in a normal upload
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["image_file"] is not None
    assert data["image_file"].endswith(".jpg")
    assert "s3" in data["image_path"]

    s3_objects = mocked_aws.list_objects_v2(Bucket="test-bucket")
    assert "Contents" in s3_objects
    assert len(s3_objects["Contents"]) == 1
    assert s3_objects["Contents"][0]["Key"].endswith(data["image_file"])


## Test Forgot Password Sends Email
@pytest.mark.anyio
async def test_forgot_password_sends_email(client: AsyncClient):
    await create_test_user(client)

    with (
        patch(
            "routers.users.send_password_reset_email",  # This is a gotcha. This file lives in email_utils.py. Patch where the function is looked up, not where it's defined.
            new_callable=AsyncMock,  # This will prevent the mock from mocking the real function in email_utils, but continue to have the local routers calling the real function, not the mock.
        ) as mock_send
    ):  # Mock where it's USED. Not where it's defined.
        response = await client.post(
            "/api/users/forgot-password",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 202
        mock_send.assert_awaited_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == "test@example.com"
        assert call_kwargs["username"] == "testuser"
        assert "token" in call_kwargs


@pytest.mark.anyio
async def test_get_current_user(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.get("/api/users/me", headers=auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert user["username"] == data["username"]


@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient, db_session: AsyncSession):
    user = await create_test_user(client)
    token = await login_user(client)

    result = await db_session.execute(
        select(models.User).where(models.User.id == user["id"])
    )
    active_user = result.scalars().first()
    assert active_user is not None

    response = await client.delete(
        f"/api/users/{user['id']}", headers=auth_header(token)
    )
    assert response.status_code == 204

    result = await db_session.execute(
        select(models.User).where(models.User.id == user["id"])
    )
    deleted_user = result.scalars().first()
    assert deleted_user is None


@pytest.mark.anyio
async def test_delete_user_not_authenticated(
    client: AsyncClient, db_session: AsyncSession
):
    user = await create_test_user(client)

    result = await db_session.execute(
        select(models.User).where(models.User.id == user["id"])
    )
    active_user = result.scalars().first()
    assert active_user is not None

    response = await client.delete(f"/api/users/{user['id']}")
    assert response.status_code == 401  


@pytest.mark.anyio
async def test_delete_different_user(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    response = await client.delete("/api/users/1123123", headers=auth_header(token))
    assert response.status_code == 403
