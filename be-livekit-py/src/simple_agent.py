from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation, openai

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions='You are a helpful voice AI assistant.',
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice='coral'),
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
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions='Greet the user and offer your assistance. Speak in japanese only.',
    )


def app():
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))