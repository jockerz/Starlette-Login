# Login Manager Configuration

## Basic Usage

```python
from starlette_login.login_manager import Config, LoginManager

config = Config(protection_level=2)
login_manager = LoginManager(redirect_to='login', config=config)
```
