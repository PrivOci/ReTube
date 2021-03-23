import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import Skeleton from "./Skeleton";
import VideoPlayer from "./VideoPlayer";

import { videoUrlDetails } from "../utils";

const VIDEO_API = "api/video/";

const VideoPage = ({ location }) => {
  const CurrentLocation = useLocation();

  let url = CurrentLocation.state
    ? CurrentLocation.state.url
    : location.search.split("url=")[1];
  url = decodeURI(url);

  let [platform, id] = videoUrlDetails(url);

  const [videoMeta, setVideoMeta] = useState(null);

  console.log(`watch: p:${platform} id:${id}`);
  useEffect(() => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        platform: platform,
        id: id,
      }),
    };
    fetch(`http://localhost:8000/${VIDEO_API}`, requestOptions)
      .then((response) => response.json())
      .then((data) => {
        console.log("video rec data:");
        console.log(data);
        if (data.ready === false) {
          console.log("failed to get video details");
          return;
        }

        var videoData = data.content;
        setVideoMeta(videoData);
        console.log(videoData);
      });
  }, [platform, id]);

  const videoProps = {
    controls: true,
    url: videoMeta ? videoMeta.stream_url : null,
    light: videoMeta ? videoMeta.thumbnail_url : null,
    // https://github.com/CookPete/react-player#props
  };

  return (
    <div className="flex justify-center">
      {!videoProps.url ? (
        <div className="w-1/2 justify-center">
          <Skeleton />
        </div>
      ) : (
        <div>
          <VideoPlayer videoProps={videoProps} details={videoMeta} />
        </div>
      )}
    </div>
  );
};

export default VideoPage;
