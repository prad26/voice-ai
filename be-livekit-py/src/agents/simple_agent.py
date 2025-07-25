import json
from datetime import datetime
from enum import Enum
from pathlib import Path

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
    bey,  # type: ignore  # noqa: F401
    google,  # type: ignore  # noqa: F401
    openai,  # type: ignore  # noqa: F401
)

load_dotenv()


class Languages(Enum):
    JAPANESE = 'Japanese'
    ENGLISH = 'English'

    @property
    def language_code(self) -> str:
        """Returns the BCP-47 Code for the language.

        Returns:
            str: The BCP-47 code for the language.
        """

        codes = {
            Languages.JAPANESE: 'ja-JP',
            Languages.ENGLISH: 'en-US',
        }

        return codes[self]


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
        )


async def entrypoint(ctx: agents.JobContext):
    agent_language = Languages.ENGLISH

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
    #     avatar_id='b9be11b8-89fb-4227-8f86-4a881393cbdb',
    # )

    # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    async def write_transcript():
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')

        project_root = Path(__file__).resolve().parent.parent.parent
        tmp_dir = project_root / 'tmp'
        tmp_dir.mkdir(exist_ok=True)
        filename = tmp_dir / f'transcript_{ctx.room.name}_{current_date}.json'

        with open(filename, 'w') as f:
            job_data = {}
            job_data['room_name'] = ctx.room.name
            job_data['timestamp'] = current_date
            job_data['job_metadata'] = ctx.job.metadata
            job_data['chat_items'] = session.history.to_dict()['items']

            json.dump(job_data, f, indent=2)

    ctx.add_shutdown_callback(write_transcript)

    await session.start(
        room=ctx.room,
        agent=HelpfulAgent(language=agent_language),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            # noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
            text_enabled=True,
        ),
    )

    background_audio = BackgroundAudioPlayer(  # noqa: F841
        ambient_sound=AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.8),
        thinking_sound=[
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.8),
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.7),
        ],
    )

    # await background_audio.start(room=ctx.room, agent_session=session)


def app():
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
