import React, { useEffect, useState } from "react";
import {
  platforms,
  humanizeDurationSec,
  timeSince,
  cleanUpUrl,
} from "../utils";
import Skeleton from "./Skeleton";
import WatchedSymbol from "./WatchedSymbol";
import { snapshot } from "valtio";
import dynamic from "next/dynamic";
const SubscribeButton = dynamic(() => import("./SubscribeButton"), {
  ssr: false,
});

const VideoThumbnail = ({ item }) => {
  const platform = platforms[item.platform];
  const [isWatched, setIsWatched] = useState(false);

  useEffect(() => {
    const proxy_data = require("./data");
    const dbWatched = snapshot(proxy_data.dbWatched);
    if (item.videoUrl) {
      const watchUrl = cleanUpUrl(item.videoUrl);
      if (dbWatched.links.includes(watchUrl)) {
        setIsWatched(true);
      }
    }
  }, []);

  return (
    <div className="inline-block align-middle overflow-hidden">
      <a href={`/watch?url=${item.videoUrl}`} alt="video source">
        <div className="relative">
          <img
            src={item.thumbnailUrl}
            alt="thumbnail"
            className="object-center rounded-xl mb-1 transition duration-300 ease-in-out hover:opacity-75"
          />
          <span className="px-2 py-1 text-white bg-gray-700 text-xs rounded absolute left-2 bottom-2 bg-opacity-50">
            {`${timeSince(item.createdAt)} ago`}
          </span>
          <span className="px-2 py-1 text-white bg-gray-700 text-xs rounded absolute right-2 bottom-2 bg-opacity-50">
            {humanizeDurationSec(item.duration)}
          </span>
          {isWatched ? (
            <span className="px-2 py-1 text-white bg-gray-700 text-xs rounded absolute left-2 top-2 bg-opacity-50">
              <WatchedSymbol withDot={false} />
            </span>
          ) : (
            <span />
          )}
        </div>
        <p className="text-xs px-1 bg-gray-200 text-gray-800 rounded-full">
          {platform}
        </p>
        <p className="text-sm py-1 text-black dark:text-white">{item.title}</p>
      </a>
      <a href={`channel?url=${item.channelUrl}`} alt="channel">
        <p className="text-xs text-gray-600 hover:text-gray-400 dark:text-gray-300">
          {item.channel}
        </p>
      </a>
    </div>
  );
};

const ChannelThumbnail = ({ item }) => {
  const platform = platforms[item.platform];

  return (
    <div className="inline-block align-middle overflow-hidden">
      <a href={`channel?url=${item.channelUrl}`} alt="video source">
        <img
          src={item.thumbnailUrl}
          alt="thumbnail"
          className="object-center rounded-2xl mb-1 transition duration-300 ease-in-out hover:opacity-75"
        />
        <p className="text-xs px-1 bg-gray-200 text-gray-800 rounded-full">
          {platform}
        </p>
      </a>
      <SubscribeButton channel_url={item.channelUrl} />
      <a href={`channel?url=${item.channelUrl}`} alt="video source">
        <p className="text-sm py-1 text-black dark:text-white">{item.title}</p>
      </a>
      <p className="text-xs text-gray-600 hover:text-black dark:text-gray-400">
        {item.creator}
      </p>
    </div>
  );
};

const videoBoxes = (item, index) => {
  return (
    <div key={index} className="lg:w-1/4 md:w-1/2 p-4 w-full">
      {item ? (
        item.isChannel ? (
          <ChannelThumbnail item={item} />
        ) : (
          <VideoThumbnail item={item} />
        )
      ) : (
        <Skeleton />
      )}
    </div>
  );
};

export default videoBoxes;
