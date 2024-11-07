# Starlette-Login

Repository: [Starlette-Login](https://github.com/jockerz/Starlette-Login)


Starlette-Login provides user session management for Starlette.

Much inspired by [Flask-Login][Flask-Login],
it handles the common tasks of logging in, logging out,
and remembering your users' sessions over extended periods of time.

Key features:

- Store the active user’s ID in the session,
  and let you log them in and out easily.
- Restrict routes to logged-in user only
- Handle **remember-me** functionality


## Installation

Stable
```shell
pip install Starlette-Login
```

Development
```shell
pip install 'git+https://github.com/jockerz/Starlette-Login'
```


## Basic Example

To run example below, please install `uvicorn`.

```shell
pip install uvicorn
```

### Models

User model and how to get the user by `username` and `id`

```python title="models.py"
--8<-- "docs_src/index/models.py"
```

### Routes

Implement `login` and `logout` **utils** and `login_required` **decorator**

```python title="routes.py"
--8<-- "docs_src/index/routes.py"
```

### Starlette Application

Using `AuthenticationMiddleware`, 
then using the `LoginManager` and set `LoginManager`'s `user_loader` 
callback function by `set_user_loader` method.


```python
--8<-- "docs_src/index/app.py"
```

**Run**

```shell
uvicorn app:app
```

**Endpoints**

 - Home: `/`
 - Login: `/login`
 - Logout: `/logout`

## More Examples

 - [Basic Auth](https://github.com/jockerz/Starlette-Login-Example/tree/main/basic_auth)
 - Token Auth: *TODO*
 - Multiple Auth: *TODO*


[Flask-Login]: https://flask-login.readthedocs.io
