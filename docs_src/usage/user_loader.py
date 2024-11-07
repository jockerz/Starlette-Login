from starlette.requests import Request

from models import User


async def get_user_by_id(request: Request, user_id: int):
    # return a sub class of `mixin.UserMixin` instance
    db = request.state.db
    user = await User.get_by_id(db, user_id)
    return user


login_manager.set_user_loader(get_user_by_id)
