import { useEffect } from "react";
import { useRouter } from "next/router";
import type { ReactElement } from "react";
import type { NextPageWithLayout } from "./_app";

const Index: NextPageWithLayout = () => {
  const router = useRouter();
  useEffect(() => {
    router.replace("/chat");
  }, [router]);
  return null;
};

// Avoid a Header/Footer flash before the redirect.
Index.getLayout = (page: ReactElement) => page;

export default Index;
