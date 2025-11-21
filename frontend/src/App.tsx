import { Route, Routes } from "react-router-dom";

import { ReasoningExplorerRoutes } from "./features/reasoning-explorer";

function Home(): JSX.Element {
  return <div>Welcome to Tax Lien Strategist.</div>;
}

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <ReasoningExplorerRoutes />
      {/* TODO: add nested routes for auth, investors, properties, liens, analysis, portfolios, documents, notifications */}
    </Routes>
  );
}
