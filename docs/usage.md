!!! info
    This page is step by step usage.


## Login Manager

First of all, you need to create a `LoginManager` instance.
The login manager manage the `Starlette-Login` behaviour of your `Starlette` instance.

```python
--8<-- "docs_src/usage/login_manager.py"
```

## User Model Class

User class must inherit `UserMixin` class.

```python title="models.py"
--8<-- "docs_src/usage/models.py"
```

## User Loader Callback

Then you will need to provide a __user loader__ callback function.

```python
--8<-- "docs_src/usage/user_loader.py"
```

## Starlette Application and Middleware

Upon creation of `Starlette` instance, we add `SessionMiddleware` and `AuthenticationMiddleware`.

`SessionMiddleware` is required to manage `http` and `websocket` session.

```python
--8<-- "docs_src/usage/app.py"
```

Then you need to add the `login manager` to `Starlette` instance `state`.

```python
app.state.login_manager = login_manager
```

## Login and Logout

Now that the `Starlette` application instance is ready to use, 
you will need to create a `login` and `logout` route to manage user authentication. 

See `routes.py` on [Basic Example](index.md) page for `login` and `logout` route example.


## Decorator

Now we can filter our _routes_ for authenticated user by using these _decorators_

`Starlette-Login` Decorator helps to prevent non-authorized user to access certain route.
There are 3 available __decorator__:

- `login_required`: only authenticated user can access the page
- `fresh_login_required`: only **newly logged-in** user can access the page
- `ws_login_required`: websocket route version of `login_required`

__Usage__

```python
--8<-- "docs_src/usage/usage.py"
```

See [tests/views.py](https://github.com/jockerz/Starlette-Login/blob/main/tests/views.py) for more decorated routes example.
