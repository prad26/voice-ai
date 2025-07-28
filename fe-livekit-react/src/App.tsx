import { ConnectionState, ControlBar } from '@livekit/components-react';
import { LiveKitRoomContext, useConnectRoom } from './lib/livekit';

export default function App() {
  return (
    <LiveKitRoomContext>
      <div className='flex flex-col items-center justify-center min-h-screen bg-gray-100'>
        <p className='text-xl'>This a LiveKit Client built in React!</p>

        <ConnectButton />

        <ConnectionState />
        <ControlBar />
      </div>
    </LiveKitRoomContext>
  );
}

function ConnectButton() {
  const connectToRoom = useConnectRoom();

  return (
    <button
      type='button'
      className='mt-4 px-4 py-2 bg-blue-500 text-white
      rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400'
      onClick={() => {
        connectToRoom();
      }}
    >
      Connect to Room
    </button>
  );
}
