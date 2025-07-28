import { useRoomContext } from '@livekit/components-react';
import { useCallback } from 'react';

const LIVEKIT_URL = 'ws://127.0.0.1:7880';
const ACCESS_TOKEN
  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ1Mjk5OTMsImlzcyI6ImRldmtleSIsIm5hbWUiOiJyZWFjdF9jbGllbnQiLCJuYmYiOjE3NTM2NjU5OTMsInN1YiI6InJlYWN0X2NsaWVudCIsInZpZGVvIjp7InJvb20iOiJyZWFjdF9yb29tIiwicm9vbUpvaW4iOnRydWV9fQ.SpvsZKG0SXp3C_EW2Ljh6Fn9OMLLZbm5Sb4Ta2JiHtk';

export function useConnectRoom() {
  const room = useRoomContext();

  const connectToRoom = useCallback(
    () => {
      room.connect(LIVEKIT_URL, ACCESS_TOKEN);
    },
    [room],
  );

  return connectToRoom;
}
