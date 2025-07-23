from enum import Enum

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.plugins import (
    google,  # type: ignore  # noqa: F401
    noise_cancellation,
    openai,
)

load_dotenv()


class Languages(Enum):
    JAPANESE = 'Japanese'
    ENGLISH = 'English'

    @property
    def language_code(self) -> str:
        return {
            Languages.JAPANESE: 'ja-JP',
            Languages.ENGLISH: 'en-US',
        }[self]


class HelpfulAgent(Agent):
    def __init__(self, language: Languages):
        super().__init__(
            instructions=f"""
                You are a helpful voice AI assistant.

                You can only speak in the {language} language.
                Even when instructed or asked in another language.
                If the user specifically asks you to speak in another language,
                you may temporarily speak in that language,
                but always return to speaking in {language} language afterwards.
            """,
        )
        self.language = language

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=f"""
                Greet the user and ask what help they need. Speak in {self.language.value} language.
                """,
            # allow_interruptions=False,
        )


async def entrypoint(ctx: agents.JobContext):
    agent_language = Languages.JAPANESE

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice='coral',
        ),
    )

    # session = AgentSession(
    #     llm=google.beta.realtime.RealtimeModel(
    #         model='gemini-2.5-flash-preview-native-audio-dialog',
    #         # model='gemini-2.0-flash-exp',
    #         voice='Leda',
    #         temperature=0.8,
    #         instructions='You are a helpful assistant.',
    #         language=agent_language.language_code,
    #     )
    # )

    # avatar = bey.AvatarSession(
    #     avatar_id="b9be11b8-89fb-4227-8f86-4a881393cbdb",
    # )

    # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=HelpfulAgent(language=agent_language),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
            text_enabled=True,
        ),
    )

    background_audio = BackgroundAudioPlayer(
        ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.8),
        thinking_sound=[
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.8),
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.7),
        ],
    )

    await background_audio.start(room=ctx.room, agent_session=session)

    await ctx.connect()


def app():
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
