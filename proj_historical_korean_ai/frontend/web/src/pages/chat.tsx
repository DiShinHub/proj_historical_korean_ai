import { useState } from "react";
import { TextField, Button } from "@mui/material";
import { Meta } from "@/layout/Meta";
import api from "@/api";

export default function ChatPage() {
  const [text, setText] = useState("");

  const handleSubmit = async () => {

    try {
      const response = await api.post(
        "/api/v1/na/prompts/",
        {
          text,
        }
      );
      console.log("STATUS", response.status);
      console.log("HEADERS", response.headers);
      console.log("DATA", response.data);

      console.log(response.data);
    } catch (e) {
      console.error("ERROR", e);
    }

  };


  return (
    <>
      <Meta title="Chat" description="Chat Page" />

      <div style={{ padding: 20 }}>
        <TextField
          fullWidth
          multiline
          rows={8}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <Button
          variant="contained"
          onClick={handleSubmit}
          style={{ marginTop: 20 }}
        >
          전송
        </Button>
      </div>
    </>
  );
}