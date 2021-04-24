import React from "react";
import ReactPlayer from "react-player";
// import Draggable from "react-draggable";
import SubscribeButton from "./SubscribeButton";
import { platforms, timeSince } from "../utils";
import { Link } from "react-router-dom";

const VideoPlayer = ({ videoProps, details, platform, url }) => {
  const platformName = platforms[platform];
  console.log(details);
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
          <p className="font-medium text-gray-600 dark:text-gray-300 hover:text-gray-400">
            <Link to={`/VideoBoard?url=${details.channelUrl}`}>
              {details.author}
            </Link>
          </p>
          <div className="flex items-center text-gray-500 dark:text-gray-400 text-md my-2 md:m-0">
            <svg
              width="10"
              height="10"
              fill="currentColor"
              className="mr-2"
              viewBox="0 0 1792 1792"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M1664 960q-152-236-381-353 61 104 61 225 0 185-131.5 316.5t-316.5 131.5-316.5-131.5-131.5-316.5q0-121 61-225-229 117-381 353 133 205 333.5 326.5t434.5 121.5 434.5-121.5 333.5-326.5zm-720-384q0-20-14-34t-34-14q-125 0-214.5 89.5t-89.5 214.5q0 20 14 34t34 14 34-14 14-34q0-86 61-147t147-61q20 0 34-14t14-34zm848 384q0 34-20 69-140 230-376.5 368.5t-499.5 138.5-499.5-139-376.5-368q-20-35-20-69t20-69q140-229 376.5-368t499.5-139 499.5 139 376.5 368q20 35 20 69z"></path>
            </svg>
            <span>{`${details.viewCount} views • ${timeSince(
              details.createdAt
            )} ago`}</span>
          </div>
          <div className="flex space-x-4">
            <SubscribeButton
              channel_url={details.channelUrl}
              count={details.subscriberCount}
            />
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
