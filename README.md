# User Management Microservice

This microservice handles user-related operations such as registration, login, role management, and user updates.

## Table of Contents
- [API Endpoints](#api-endpoints)
  - [GET /](#get)
  - [POST /register](#post-register)
  - [POST /login](#post-login)
  - [GET /users](#get-users)
  - [PATCH /users/{id}](#patch-usersid)
  - [PATCH /users/{id}/add-role](#patch-usersidadd-role)
  - [PATCH /users/{id}/remove-role](#patch-usersidremove-role)
  - [DELETE /users/{id}](#delete-usersid)
  - [POST /logout](#post-logout)
  - [GET /health](#get-health)
- [Error Handling](#error-handling)
- [License](#license)

## API Endpoints

### GET /
- **Description**: Provides service information.
- **Example Request**:
    ```http
    GET /
    ```
- **Response**:
    ```json
    {
        "service": "User Management Microservice",
        "description": "This microservice handles user-related operations such as registration, login, role management, and user updates.",
        "endpoints": [
            {
                "path": "/register",
                "method": "POST",
                "description": "Register a new user",
                "response": "JSON object with success or error message",
                "role_required": "none"
            },
            ...
        ]
    }
    ```
- **Response Codes**: `200`, `500`

### POST /register
- **Description**: Register a new user.
- **Example Request**:
    ```http
    POST /register
    Content-Type: application/json

    {
        "email": "user@example.com",
        "password": "password123"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User registered successfully."
    }
    ```
- **Response Codes**: `201`, `400`, `500`

### POST /login
- **Description**: Authenticate an existing user.
- **Example Request**:
    ```http
    POST /login
    Content-Type: application/json

    {
        "email": "user@example.com",
        "password": "password123"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Login successful.",
        "Authorization": "Bearer <token>"
    }
    ```
- **Response Codes**: `200`, `400`, `401`, `500`

### GET /users
- **Description**: Retrieve all users (admin role required).
- **Example Request**:
    ```http
    GET /users
    ```
- **Response**:
    ```json
    [
        {
            "id": 1,
            "email": "user@example.com",
            "roles": ["admin"]
        },
        ...
    ]
    ```
- **Response Codes**: `200`, `403`, `500`

### PATCH /users/{id}
- **Description**: Update user information (admin role required).
- **Example Request**:
    ```http
    PATCH /users/1
    Content-Type: application/json

    {
        "email": "newemail@example.com"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User updated successfully."
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### PATCH /users/{id}/add-role
- **Description**: Add a role to a user (admin role required).
- **Example Request**:
    ```http
    PATCH /users/1/add-role
    Content-Type: application/json

    {
        "new_role": "admin"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Role added successfully."
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### PATCH /users/{id}/remove-role
- **Description**: Remove a role from a user (admin role required).
- **Example Request**:
    ```http
    PATCH /users/1/remove-role
    Content-Type: application/json

    {
        "remove_role": "user"
    }
    ```
- **Response**:
    ```json
    {
        "message": "Role removed successfully."
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### DELETE /users/{id}
- **Description**: Delete a user by ID (admin role required).
- **Example Request**:
    ```http
    DELETE /users/1
    ```
- **Response**:
    ```json
    {
        "message": "User deleted successfully."
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### POST /logout
- **Description**: Log out the user.
- **Example Request**:
    ```http
    POST /logout
    ```
- **Response**:
    ```json
    {
        "message": "Logout successful."
    }
    ```
- **Response Codes**: `200`

### GET /health
- **Description**: Check the health status of the microservice.
- **Example Request**:
    ```http
    GET /health
    ```
- **Response**:
    ```json
    {
        "status": "healthy"
    }
    ```
- **Response Codes**: `200`

## Error Handling

Handles unmatched endpoints and method errors:

### 404 Error
- **Description**: Endpoint does not exist.
- **Example Response**:
    ```json
    {
        "message": "Endpoint does not exist."
    }
    ```

### 405 Error
- **Description**: Method not allowed - double check the method you are using.
- **Example Response**:
    ```json
    {
        "message": "Method not allowed - double check the method you are using."
    }
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
