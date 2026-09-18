from fastapi import APIRouter

from models.group_request import DBGroupRequest


router = APIRouter(prefix="/group-requests", tags=["Group Requests"])
