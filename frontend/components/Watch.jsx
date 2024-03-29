import React from "react";

import { useRouter } from "next/router";
import useSWR from "swr";

import Skeleton from "./Skeleton";
import VideoPlayer from "./VideoPlayer";

import { videoUrlDetails } from "../utils";

const VIDEO_API = "api/video/";
// TODO: extract
const BACKEND_ADDR = "http://localhost:8000";

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
  return fetch(`${BACKEND_ADDR}/${VIDEO_API}`, requestOptions)
    .then((response) => response.json())
    .then((data) => {
      if (data.ready === false) {
        console.log("failed to get video details");
        return {};
      }
      return data.content;
    });
};

const Watch = () => {
  const router = useRouter();

  // TODO: standartize original URL (targetUrl)
  let targetUrl = router.asPath.split("url=")[1];
  let [platform, id] = videoUrlDetails(targetUrl);
  
  console.log(`watch: p:${platform} id:${id}`);
  const { data } = useSWR(JSON.stringify({ platform, id }), fetchVideoMetaSWR, {
    revalidateOnFocus: false,
    refreshWhenHidden: false,
    refreshInterval: 0,
  });

  const videoProps = {
    controls: true,
    url: data ? data.streamUrl : null,
    // light: data ? (data.thumbnailUrl ? data.thumbnailUrl : null) : null,
    // https://github.com/CookPete/react-player#props
  };
  return (
    <div className="container mx-auto">
      {!data || !videoProps.url ? (
        <div className="w-1/2 justify-center">
          <Skeleton />
        </div>
      ) : (
        <div>
          <VideoPlayer
            videoProps={videoProps}
            details={data}
            platform={platform}
            originalUrl={targetUrl}
          />
        </div>
      )}
    </div>
  );
};

export default Watch;
