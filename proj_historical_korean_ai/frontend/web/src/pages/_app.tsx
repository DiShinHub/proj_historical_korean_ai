// src/pages/_app.tsx
import type { ReactElement, ReactNode } from "react";
import type { NextPage } from "next";
import type { AppProps } from "next/app";
import { I18nextProvider } from "react-i18next";
import { Provider as ReduxProvider } from "react-redux";
import { AppThemeProvider } from "../themes/ThemeContext";
import { PersistGate } from "redux-persist/integration/react";
import { Base } from "@/templates/base";
import store, { persistor } from "../redux/store";

import "@/styles/globals.css";
import "highlight.js/styles/github-dark.css";

// Import your i18n configuration
import i18n from "../i18n";

export type NextPageWithLayout<P = Record<string, unknown>> = NextPage<P> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

const BoilerplateApp = ({ Component, pageProps }: AppPropsWithLayout) => {
  // Pages may opt out of the Header/Footer shell via getLayout (e.g. /chat).
  const getLayout =
    Component.getLayout ?? ((page: ReactElement) => <Base>{page}</Base>);

  return (
    <ReduxProvider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <AppThemeProvider>
          <I18nextProvider i18n={i18n}>
            {getLayout(<Component {...pageProps} />)}
          </I18nextProvider>
        </AppThemeProvider>
      </PersistGate>
    </ReduxProvider>
  );
};

export default BoilerplateApp;
