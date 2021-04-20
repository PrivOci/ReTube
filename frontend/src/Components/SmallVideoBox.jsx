import React from "react";
import { platforms } from "../utils";
import Skeleton from "./Skeleton";
import SubscribeButton from "./SubscribeButton";

const VideoThumbnail = ({ item }) => {
  const platform = platforms[item.platform];
  // console.log(item);
  return (
    <div className="each mb-10 m-2 inline-block align-middle">
      <a href={`/watch?url=${item.videoUrl}`} alt="video source">
        <img
          src={item.thumbSrc}
          alt="thumbnail"
          className="object-center rounded-2xl mb-1 transition duration-300 ease-in-out hover:opacity-75"
        />
        <p className="text-xs px-1 bg-gray-200 text-gray-800 rounded-full">
          {platform}
        </p>
        <p className="text-sm py-1 text-black dark:text-white">{item.title}</p>
      </a>

      {/* <a href={`videolist?url=${item.channelUrl}`} alt="channel"> */}
      <p className="text-xs text-gray-600 hover:text-black dark:text-gray-400">
        {item.channel}
      </p>
      {/* </a> */}
    </div>
  );
};

const ChannelThumbnail = ({ item }) => {
  const platform = platforms[item.platform];
  // console.log(item);
  return (
    <div className="each mb-10 m-2 inline-block align-middle">
      <a href={`videolist?url=${item.channelUrl}`} alt="video source">
        <img
          src={item.thumbSrc}
          alt="thumbnail"
          className="object-center rounded-2xl mb-1 transition duration-300 ease-in-out hover:opacity-75"
        />
        <p className="text-xs px-1 bg-gray-200 text-gray-800 rounded-full">
          {platform}
        </p>
      </a>
      <SubscribeButton channel_url={item.channelUrl} />
      <a href={`videolist?url=${item.channelUrl}`} alt="video source">
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
    <div key={index} className="w-full max-w-xs text-center">
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
