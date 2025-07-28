import type { ReactNode } from 'react';
import { RoomAudioRenderer, RoomContext } from '@livekit/components-react';
import { Room } from 'livekit-client';
import { useState } from 'react';
import '@livekit/components-styles';

export function LiveKitRoomContext({ children }: { children: ReactNode }) {
  const [room] = useState(() => new Room({}));

  return (
    <RoomContext value={room} data-lk-theme='default'>
      {children}
      <RoomAudioRenderer />
    </RoomContext>
  );
}
