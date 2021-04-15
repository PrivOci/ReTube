import React from "react";
import ReactPlayer from "react-player";
// import Draggable from "react-draggable";
import SubscribeButton from "./SubscribeButton";
import { platforms } from "../utils";

const VideoPlayer = ({ videoProps, details, platform, url }) => {
  const platformName = platforms[platform];

  return (
    <div className="grid grid-cols-1">
      <div className="shadow-lg justify-center rounded-2xl p-4 bg-white dark:bg-gray-700 w-full">
        <div className="aspect-w-16 aspect-h-9 lg:aspect-none flex justify-center">
          <ReactPlayer {...videoProps} width="100%" height="100%" />
        </div>
        <div className="pt-3">
          <h3 className="mr-10 text-lg truncate-2nd text-black dark:text-white antialiased sm:subpixel-antialiased md:antialiased">
            {details.title}
          </h3>
          <p className="text-md text-gray-500">
            <a
              href={`/videolist?url=${details.channel_url}`}
              alt="channel"
              className="hover:underline hover:text-blue-500"
            >
              {details.author}
            </a>
          </p>
          <h3 className="mr-10 text-md text-black dark:text-white antialiased sm:subpixel-antialiased md:antialiased">
            {details.view_count} views
          </h3>

          <div className="flex space-x-4">
            <SubscribeButton channel_url={details.channel_url} count={details.subscriber_count}/>
            <button
              className="items-center shadow bg-red-500 mt-2 px-4 py-2 text-white hover:bg-red-400 rounded-lg"
              onClick={() => window.open(url, "_blank")}
            >
              Watch On {platformName}
            </button>
          </div>
        </div>
      </div>

      <div className="shadow-lg justify-center rounded-2xl p-4 mt-2 bg-white dark:bg-gray-700 w-full text-black dark:text-white">
        <div className="whitespace-pre-line">{details.description}</div>
      </div>
    </div>
  );
};

export default VideoPlayer;
