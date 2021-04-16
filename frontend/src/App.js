import React, { useEffect } from "react";

import VideoList from "./Components/VideoList";
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
import subscriptions from "./store";
import JsonEdit from "./Components/JsonEdit";

const pages = [
  {
    name: "Popular",
    faIcon: faFire,
    path: "/videolist?url=popular",
    component: VideoList,
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
  //   path: "/videolist?url=yt_popular",
  //   component: VideoList,
  // },
  // {
  //   name: "Lbry Popular",
  //   faIcon: faFire,
  //   path: "/videolist?url=lbry_popular",
  //   component: VideoList,
  // },
  // {
  //   name: "BitChute Popular",
  //   faIcon: faFire,
  //   path: "/videolist?url=bitchute_popular",
  //   component: VideoList,
  // },
];

const ContentPages = [
  {
    path: "/videolist",
    component: VideoList,
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
  const storeReadOnly = useSnapshot(subscriptions);

  useEffect(() => {
    localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
    console.log("subscriptions Changed");
    return () => {};
  }, [storeReadOnly]);

  return (
    <div className="bg-gray-100 dark:bg-gray-600">
      <Route>
        <Bar />
        <main className="flex bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-hidden relative">
          <Sidebar pages={pages} location={location} />
          <Content>
            <Route exact path="/">
              <Redirect to="/videolist?url=popular" />
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
