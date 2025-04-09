import os

from dotenv import load_dotenv

load_dotenv("config.env")

storage = {}
api_image = os.getenv("api_image")
api_gpt = os.getenv("api_gpt")
ip_to_web_app = os.getenv("IpToWebApp")
token = os.getenv('ApiToken')
__checking__ = os.getenv("checking")