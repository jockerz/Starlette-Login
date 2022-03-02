# Login Manager Configuration

## Basic Usage

```python
from starlette_login.login_manager import (
    Config, LoginManager, ProtectionLevel
)

config = Config(protection_level=ProtectionLevel.Strong)
login_manager = LoginManager(redirect_to='login', config=config)
```
