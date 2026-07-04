import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { SocketStatus } from "@/lib/socket";

interface SocketState {
  status: SocketStatus;
}

const initialState: SocketState = {
  status: "idle",
};

const socketSlice = createSlice({
  name: "socket",
  initialState,
  reducers: {
    setSocketStatus(state, action: PayloadAction<SocketStatus>) {
      state.status = action.payload;
    },
  },
});

export const { setSocketStatus } = socketSlice.actions;
export default socketSlice.reducer;
