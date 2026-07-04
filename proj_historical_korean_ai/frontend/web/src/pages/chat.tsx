import type { ReactElement } from "react";
import Head from "next/head";
import ChatApp from "@/components/chat/ChatApp";
import type { NextPageWithLayout } from "./_app";

const ChatPage: NextPageWithLayout = () => {
  return (
    <>
      <Head>
        <title>고대 한국어 번역 LLM</title>
      </Head>
      <ChatApp />
    </>
  );
};

// Full-bleed: skip the global Header/Footer shell.
ChatPage.getLayout = (page: ReactElement) => page;

export default ChatPage;
