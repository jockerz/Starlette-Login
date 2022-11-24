## Excluded Path (Incomplete)

### Note

`request.user` call will lead to 
`AssertionError: AuthenticationMiddleware must be installed to access request.user`.
Our authentication middleware is ignoring the excluded path 
and `request.user` is not being set. 
The exception raised by `starlette`.
You do not need to use `AuthenticationMiddleware` except you need to.
