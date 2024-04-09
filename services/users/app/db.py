import os
import uuid
import logging

from tortoise.contrib.fastapi import register_tortoise
from aerich import Command
from fastapi import FastAPI

from app import settings