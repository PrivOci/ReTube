import React, { useEffect, useState } from "react";
import videoBoxes from "./SmallVideoBox";
import { fetchVideos } from "../utils";
import { snapshot } from "valtio";
import VideoBoard from "./VideoBoard";

const isFromToday = (videoEntry) => {
  const oneDay = 24 * 60 * 60 * 1000;
  const now = new Date();
  const videoDate = new Date(videoEntry.createdAt);
  const isMoreThanADay = now - videoDate > oneDay;
  if (!isMoreThanADay) {
    return true;
  }
  return false;
};

const fetchSubsVideos = async (subsStore, setVideoDataState) => {
  let allSubsWait = [];
  let allSubs = {};
  allSubs.platform = "subscriptions";
  allSubs.ready = false;
  allSubs.content = [];
  // youtube
  subsStore.youtube.forEach((item, index) => {
    const ytUrl = `https://www.youtube.com/channel/${item}`;
    allSubsWait.push(fetchVideos(ytUrl));
  });
  // Lbry
  subsStore.lbry.forEach((item, index) => {
    const lbUrl = `https://odysee.com/@${item}`;
    allSubsWait.push(fetchVideos(lbUrl));
  });
  // bitchute
  subsStore.bitchute.forEach((item, index) => {
    const bcUrl = `https://www.bitchute.com/channel/${item}`;
    allSubsWait.push(fetchVideos(bcUrl));
  });
  // rumble
  if ("rumble" in subsStore) {
    subsStore.rumble.forEach((item, index) => {
      const rbUrl = `https://rumble.com/${item}`;
      allSubsWait.push(fetchVideos(rbUrl));
    });
  }

  for (const waitSub of allSubsWait) {
    if (waitSub === null) {
      continue;
    }
    const result = await waitSub;
    if (result === null) {
      continue;
    }
    if (result.ready === "False") {
      continue;
    }
    let videoEntries = result.content;
    if (!videoEntries) continue;
    videoEntries = videoEntries.filter(isFromToday);
    allSubs.content = allSubs.content.concat(videoEntries);

    setVideoDataState();
    setVideoDataState(allSubs);
  }

  allSubs.content = allSubs.content.sort((a, b) => {
    return b.createdAt - a.createdAt;
  });
  allSubs.ready = true;
  setVideoDataState();
  setVideoDataState(allSubs);
};

const Subscriptions = () => {
  let [videoData, setVideoDataState] = useState();

  useEffect(() => {
    const proxy_data = require("./data");
    let subsStore = snapshot(proxy_data.subscriptions);
    localStorage.setItem(
      "subscriptions",
      JSON.stringify(proxy_data.subscriptions)
    );

    fetchSubsVideos(subsStore, setVideoDataState);

    return () => {
      setVideoDataState([]);
    };
  }, []);

  return <VideoBoard data={videoData} />;
};

export default Subscriptions;
