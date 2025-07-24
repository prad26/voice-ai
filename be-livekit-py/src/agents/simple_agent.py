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

                Affect: A gentle, curious narrator with a British accent, guiding a magical,
                child-friendly adventure through a fairy tale world.
                Tone: Magical, warm, and inviting, creating a sense of wonder and excitement
                for young listeners.
                Pacing: Steady and measured, with slight pauses to emphasize magical moments
                and maintain the storytelling flow.
                Emotion: Wonder, curiosity, and a sense of adventure, with a lighthearted
                and positive vibe throughout.
                Pronunciation: Clear and precise, with an emphasis on storytelling,
                ensuring the words are easy to follow and enchanting to listen to.
            """,
        )
        self.language = language

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=f"""
                Greet the user and ask what help they need. Speak in {self.language.value} language.
                """,
        )

        # await self.session.generate_reply(
        #     instructions="""
        #         Read the below exactly.

        #         むかしむかし、ある小さな森の中に、魔法の泉がひっそりと輝いていました。
        #         その泉の水を飲むと、どんな願いもひとつ叶うと言われていたんです。
        #         ある日、心優しい小さな妖精のララが、その泉を探しに旅に出ました。
        #         森の奥深く、キラキラ光る小道を進んでいくと、突然、大きなフクロウが現れて、
        #         「この先には勇気が試されるぞ」と言いました。
        #         ララは少し怖かったけれど、勇気を振り絞って「私は心からの願いを叶えたいの」と答えました。  # noqa: E501
        #         すると、フクロウはにっこり笑って道を開け、ララは無事に泉へたどり着きました。
        #         """,
        # )


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
    #     avatar_id='b9be11b8-89fb-4227-8f86-4a881393cbdb',
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

    await ctx.connect()


def app():
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
