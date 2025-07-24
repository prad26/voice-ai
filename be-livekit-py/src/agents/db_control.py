import json

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    RoomInputOptions,
    ToolError,
    WorkerOptions,
    cli,
    function_tool,
    get_job_context,
)
from livekit.plugins import (
    google,  # type: ignore  # noqa: F401
    openai,
)

load_dotenv()


class DBAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                You are a helpful voice AI assistant.

                You are a voice agent that can assist with setting the width and height of ladder.
                You are to use the given tools only and not perform any other actions.
                Another action you can perform is to set the no of steps in the ladder.
                Currently, you do not have any other controls apart from width and height.
                If the user asks for any other controls, tell this is still in development,
                and it may or may not be implemented in the future.

                Speak only in English or Japanese language, based on what the user speaks.
                Initially, you will speak in English.
                If the user speaks in Japanese, you will switch to Japanese.
            """,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
                Greet the user and ask what help they need.
                Initially, speak in English language.
                If the user speaks in Japanese, switch to Japanese language.
                """,
            # allow_interruptions=False,
        )

    @function_tool()
    async def set_step_width(self, width: float) -> None:
        """Set the width of each step of the ladder.

        Args:
            width (float): The width of each step.
        """

        try:
            room = get_job_context().room
            participant_identity = next(iter(room.remote_participants))
            print(f'Setting step width to {width} for participant {participant_identity}')

            await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method='setStepWidth',
                payload=json.dumps({'width': width}),
            )

            await self.session.generate_reply(instructions=f'Step width set to {width}')
        except Exception:
            raise ToolError('Unable to set step width')  # noqa: B904

    @function_tool()
    async def set_step_height(self, height: float) -> None:
        """Set the height of each step of the ladder.

        Args:
            height (float): The height of each step.
        """

        try:
            room = get_job_context().room
            participant_identity = next(iter(room.remote_participants))
            print(f'Setting step height to {height} for participant {participant_identity}')

            await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method='setStepHeight',
                payload=json.dumps({'height': height}),
            )

            await self.session.generate_reply(instructions=f'Step height set to {height}')
        except Exception:
            raise ToolError('Unable to set step height')  # noqa: B904

    @function_tool()
    async def set_no_of_steps(self, no_of_steps: int) -> None:
        """Set the number of steps in the ladder.

        Args:
            no_of_steps (int): The number of steps in the ladder.
        """

        try:
            room = get_job_context().room
            participant_identity = next(iter(room.remote_participants))
            print(
                f'Setting number of steps to {no_of_steps} for participant {participant_identity}'
            )

            await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method='setNoOfSteps',
                payload=json.dumps({'noOfSteps': no_of_steps}),
            )

            await self.session.generate_reply(instructions=f'Number of steps set to {no_of_steps}')
        except Exception:
            raise ToolError('Unable to set number of steps')  # noqa: B904


async def entrypoint(ctx: agents.JobContext):
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
    #     )
    # )

    # avatar = bey.AvatarSession(
    #     avatar_id="b9be11b8-89fb-4227-8f86-4a881393cbdb",
    # )

    # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=DBAgent(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            # noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
            text_enabled=False,
        ),
    )

    await ctx.connect()


def app():
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )
