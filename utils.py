from pyrogram.types import Message
from pyrogram import Client
from asyncio import wait_for, TimeoutError
from pyrogram.filters import private, user


async def listen(client: Client, user_id: int, timeout: int = 60) -> Message:
    """
    Custom listen function to wait for a user's reply.
    :param client: Pyrogram Client instance
    :param user_id: User ID to listen to
    :param timeout: Time in seconds to wait for a response
    :return: Message object
    :raises TimeoutError: If the user doesn't respond within the timeout period
    """
    try:
        response = await wait_for(
            client.listen(filters=private & user(user_id)),
            timeout=timeout
        )
        return response
    except TimeoutError:
        raise TimeoutError("User did not respond in time.")
