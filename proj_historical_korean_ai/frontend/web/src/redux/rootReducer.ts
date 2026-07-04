// src/redux/rootReducer.ts
import { persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";
import { combineReducers } from "@reduxjs/toolkit";
import postReducer from "./posts/reducer";
import authReducer from "./slices/authSlice";
import sessionsReducer from "./slices/sessionsSlice";
import messagesReducer from "./slices/messagesSlice";
import socketReducer from "./slices/socketSlice";

const persistConfig = {
  key: "root",
  storage,
  // Chat state is always refetched from the backend; nothing is persisted.
  whitelist: [],
};

const rootReducer = combineReducers({
  posts: postReducer,
  auth: authReducer,
  sessions: sessionsReducer,
  messages: messagesReducer,
  socket: socketReducer,
});

export default persistReducer(persistConfig, rootReducer);
