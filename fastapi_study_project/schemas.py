from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
    # allows returning data as attribute.
    # (user.id / user.username / user.email)


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
