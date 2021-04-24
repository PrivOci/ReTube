import React, { useEffect } from "react";

import VideoBoard from "./Components/VideoBoard";
import VideoPage from "./Components/CurrentVideo";
import { useLocation, Redirect } from "react-router-dom";

import Bar from "./Components/Bar";
import Sidebar from "./Components/Sidebar";
import Content from "./Components/Content";
import Footer from "./Components/footer";
import VideoPlayer from "./Components/VideoPlayer";
import Subscriptions from "./Components/Subscriptions";
import Settings from "./Components/Settings";

import { Route } from "react-router-dom";

import { faFire, faNewspaper, faEdit } from "@fortawesome/free-solid-svg-icons";

import { useSnapshot } from "valtio";
import { subscriptions } from "./Components/data";
import { config } from "./Components/data";
import JsonEdit from "./Components/JsonEdit";

const pages = [
  {
    name: "Popular",
    faIcon: faFire,
    path: "/VideoBoard?url=popular",
    component: VideoBoard,
  },
  {
    name: "Subscriptions",
    faIcon: faNewspaper,
    path: "/subscriptions",
    component: Subscriptions,
  },
  {
    name: "JSON View",
    faIcon: faEdit,
    path: "/json",
    component: JsonEdit,
  },
  //// testing
  // {
  //   name: "YT Popular",
  //   faIcon: faFire,
  //   path: "/VideoBoard?url=yt_popular",
  //   component: VideoBoard,
  // },
  // {
  //   name: "Lbry Popular",
  //   faIcon: faFire,
  //   path: "/VideoBoard?url=lbry_popular",
  //   component: VideoBoard,
  // },
  // {
  //   name: "BitChute Popular",
  //   faIcon: faFire,
  //   path: "/VideoBoard?url=bitchute_popular",
  //   component: VideoBoard,
  // },
];

const ContentPages = [
  {
    path: "/VideoBoard",
    component: VideoBoard,
  },
  {
    path: "/watch",
    component: VideoPage,
  },
  {
    path: "/VideoPlayer",
    component: VideoPlayer,
  },
  {
    path: "/subscriptions",
    component: Subscriptions,
  },
  {
    path: "/json",
    component: JsonEdit,
  },
  {
    path: "/settings",
    component: Settings,
  },
];

function App() {
  const location = useLocation();
  const subsReadOnly = useSnapshot(subscriptions);
  const configReadOnly = useSnapshot(config);

  useEffect(() => {
    localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
    localStorage.setItem("config", JSON.stringify(configReadOnly));
    console.log("subscriptions/config changed");
    return () => {};
  }, [subsReadOnly, configReadOnly]);

  return (
    <div className="bg-gray-100 dark:bg-gray-600">
      <Route>
        <Bar />
        <main className="flex bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-hidden relative">
          <Sidebar pages={pages} location={location} />
          <Content>
            <Route exact path="/">
              <Redirect to="/VideoBoard?url=popular" />
            </Route>
            {ContentPages.map((page, index) => {
              return (
                <Route
                  exact
                  path={page.path}
                  key={index}
                  component={page.component}
                />
              );
            })}
          </Content>
        </main>
        <Footer />
      </Route>
    </div>
  );
}

export default App;
