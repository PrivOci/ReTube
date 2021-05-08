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

    allPopular.content = (await ytPromise).content.slice(1, 10);
    setVideoDataState(allPopular);
    allPopular.content = allPopular.content.concat(
      (await lbPromise).content.slice(1, 10)
    );
    setVideoDataState();
    setVideoDataState(allPopular);
    allPopular.content = allPopular.content.concat(
      (await bcPromise).content.slice(1, 10)
    );
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
