import React, { useEffect, useState } from "react";
import { fetchVideos } from "../utils";
import VideoBoard from "../components/VideoBoard";
export default function popular() {
  let [videoData, setVideoDataState] = useState();

  const fetchPopularVideos = async (setVideoDataState) => {
    console.log("fetchPopularVideos");
    const ytPromise = fetchVideos("yt_popular");
    const lbPromise = fetchVideos("lbry_popular");
    const bcPromise = fetchVideos("bitchute_popular");

    let allPopular = {};
    allPopular.platform = "all";
    allPopular.ready = false;
    allPopular.content = [];

    const ytResults = await ytPromise;
    if (ytResults) {
      allPopular.content = ytResults.content.slice(1, 10);
      setVideoDataState(allPopular);
    }

    const lbryResults = await lbPromise;
    if (lbryResults) {
      allPopular.content = allPopular.content.concat(
        lbryResults.content.slice(1, 10)
      );
      setVideoDataState();
      setVideoDataState(allPopular);
    }

    const bcResults = await bcPromise;
    if (bcResults) {
      allPopular.content = allPopular.content.concat(
        bcResults.content.slice(1, 10)
      );
      setVideoDataState();
      setVideoDataState(allPopular);
    }

    allPopular.ready = true;
    setVideoDataState();
    setVideoDataState(allPopular);
  };

  useEffect(() => {
    fetchPopularVideos(setVideoDataState);

    return () => {
      setVideoDataState([]);
    };
  }, []);

  return (
    <div>
      {/* TODO */}
      <VideoBoard data={videoData} />
    </div>
  );
}
