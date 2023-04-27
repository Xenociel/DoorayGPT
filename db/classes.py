from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

class Dooray(BaseModel):
    tenantId: str
    tenantDomain: str
    channelId: str
    channelName: str
    userId: str
    command: str
    text: str
    responseUrl: str
    appToken: str
    cmdToken: str
    triggerId: str
