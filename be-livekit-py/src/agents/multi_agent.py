from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    RoomInputOptions,
    function_tool,
    get_job_context,
)
from livekit.plugins import noise_cancellation, openai

load_dotenv()


class ConsentCollector(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                Your are a voice AI agent with the singular task to collect positive
                recording consent from the user. If consent is not given, you must end the call.
            """
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions='Ask the user: "May I record this call for quality assurance purposes?"'
        )

    @function_tool()
    async def on_consent_given(self):
        """Use this tool to indicate that consent has been given and the call may proceed."""

        # Perform a handoff, immediately transfering control to the new agent
        return Assistant(chat_ctx=self.session.history)

    @function_tool()
    async def end_call(self) -> None:
        """Use this tool to indicate that consent has not been given and the call should end."""
        await self.session.generate_reply(
            instructions="""
                Say "Thank you for your time, have a wonderful day.",
                and then end the call.
            """
        )
        job_ctx = get_job_context()
        # delete the room to end the call
        await job_ctx.room.disconnect()


class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext) -> None:
        print(f'Creating assistant with chat context: {chat_ctx}')

        super().__init__(
            instructions="""
                You are a helpful voice AI assistant.
                You can speak only in English language.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions='Greet the user and offer your assistance in English language.'
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice='ash'),
    )

    # session = AgentSession(
    #     llm=google.beta.realtime.RealtimeModel(
    #         # model="gemini-2.5-flash-preview-native-audio-dialog",
    #         model="gemini-2.0-flash-exp",
    #         voice="Leda",
    #         temperature=0.8,
    #         instructions="You are a helpful assistant.",
    #     )
    # )

    # avatar = bey.AvatarSession(
    #     avatar_id="b9be11b8-89fb-4227-8f86-4a881393cbdb",
    # )

    # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=ConsentCollector(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
        ),
    )

    await ctx.connect()

    # await session.generate_reply(
    #     instructions='Greet the user and offer your assistance. In english language.',
    # )


def app():
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
