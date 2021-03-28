import React from "react";
import { useLocation } from "react-router-dom";
import useSWR from "swr";

import Skeleton from "./Skeleton";
import VideoPlayer from "./VideoPlayer";

import { videoUrlDetails } from "../utils";

const VIDEO_API = "api/video/";

const fetchVideoMetaSWR = async (platform_id) => {
  const { platform, id } = JSON.parse(platform_id);

  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      platform: platform,
      id: id,
    }),
  };
  return fetch(`http://localhost:8000/${VIDEO_API}`, requestOptions)
    .then((response) => response.json())
    .then((data) => {
      if (data.ready === false) {
        console.log("failed to get video details");
        return {};
      }

      return data.content;
    });
};

const VideoPage = ({ location }) => {
  const CurrentLocation = useLocation();

  let url = CurrentLocation.state
    ? CurrentLocation.state.url
    : location.search.split("url=")[1];
  url = decodeURI(url);

  let [platform, id] = videoUrlDetails(url);

  console.log(`watch: p:${platform} id:${id}`);

  const { data } = useSWR(
    JSON.stringify({ platform, id }),
    fetchVideoMetaSWR
  );
  
  const videoProps = {
    controls: true,
    url: data ? data.stream_url : null,
    light: data ? data.thumbnail_url : null,
    // https://github.com/CookPete/react-player#props
  };

  return (
    <div className="flex justify-center">
      {!data || !videoProps.url ? (
        <div className="w-1/2 justify-center">
          <Skeleton />
        </div>
      ) : (
        <div>
          <VideoPlayer videoProps={videoProps} details={data} />
        </div>
      )}
    </div>
  );
};

export default VideoPage;
