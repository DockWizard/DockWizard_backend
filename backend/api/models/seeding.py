from fastapi import APIRouter, Request
from database import get_db_data
import random
import datetime


# Create a seding script that generates some data and sends it to the database
# This script should be run a 100 times

# Create a router

# Create a function that generates dummy data
# The data should be on the same format as the data that is sent from the agent
# The data should be sent to the database


def generate_dummy_data(request: Request):
    db = get_db_data(request)
