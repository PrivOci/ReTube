import React from "react";
import { platforms } from "../utils";
import Skeleton from "./Skeleton";

const VideoThumbnail = ({ videoSrc, thumbSrc, title, creator, platform }) => {
  platform = platforms[platform];

  return (
    <div className="each mb-10 m-2">
      <a href={`/watch?url=${videoSrc}`} alt="video source">
        <img
          src={thumbSrc}
          alt="thumbnail"
          className="object-center rounded-2xl mb-1 transition duration-300 ease-in-out hover:opacity-75"
        />
        <p className="text-xs px-1 bg-gray-200 text-gray-800 rounded-full">
          {platform}
        </p>
        <p className="text-sm py-1 text-black dark:text-white">{title}</p>
      </a>

      <p className="text-xs text-gray-600 hover:text-black dark:text-grey">{creator}</p>
    </div>
  );
};

const videoBoxes = (item, index) => {
  return (
    <div key={index} className="w-full max-w-xs text-center">
      {item ? (
        <VideoThumbnail
          videoSrc={item.videoUrl}
          thumbSrc={item.thumbSrc}
          title={item.title}
          creator={item.channel}
          platform={item.platform}
        />
      ) : (
        <Skeleton />
      )}
    </div>
  );
};

export default videoBoxes;
