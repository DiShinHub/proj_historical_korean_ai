import type { ReactElement } from "react";
import Head from "next/head";
import DictionaryApp from "@/components/dictionary/DictionaryApp";
import type { NextPageWithLayout } from "./_app";

const DictionaryPage: NextPageWithLayout = () => {
  return (
    <>
      <Head>
        <title>고어 사전 관리 · 고대 한국어 번역 LLM</title>
      </Head>
      <DictionaryApp />
    </>
  );
};

// 채팅 화면과 마찬가지로 전체 화면을 쓰므로 Header/Footer 셸을 건너뛴다.
DictionaryPage.getLayout = (page: ReactElement) => page;

export default DictionaryPage;
