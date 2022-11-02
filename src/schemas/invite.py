from pydantic import BaseModel


class InviteFrom(BaseModel):
    id: int
    title: str


class Invite(BaseModel):
    id: int
    accepted: bool
    rejected: bool
    company: InviteFrom
