from openai import OpenAI
from langchain import prompts
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

from config import MODEL_NAME


@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(model=MODEL_NAME)
    prompt = prompts.ChatPromptTemplate.from_messages([
        ("system", "You imitate the way I talk. Your name is FGK, you're a Data Science graduate student at BU."),
        ("user", "{input}")

    ])
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")

    msg = cl.Message(content="")

    for chunk in await cl.make_async(runnable.stream)(
        {"input": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()