import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Header from "./components/common/Header";
import HomePage from "./pages/HomePage";
import TutorialPage from "./pages/TutorialPage";
import EpisodeListPage from "./pages/EpisodeListPage";
import PlayPage from "./pages/PlayPage";
import ResultPage from "./pages/ResultPage";
import ProfilePage from "./pages/ProfilePage";

function App() {
  return (
    <BrowserRouter>

      <Header />

      <Routes>

        <Route
          path="/"
          element={<HomePage />}
        />

        <Route
          path="/tutorial"
          element={<TutorialPage />}
        />

        <Route
          path="/episodes"
          element={<EpisodeListPage />}
        />

        <Route
          path="/play/:episodeId"
          element={<PlayPage />}
        />

        <Route
          path="/result"
          element={<ResultPage />}
        />

        <Route
          path="/profile"
          element={<ProfilePage />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;