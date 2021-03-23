import React from "react";
import ReactPlayer from "react-player";
// import Draggable from "react-draggable";
import SubscribeButton from "./SubscribeButton"

const VideoPlayer = ({ videoProps, details }) => {
  return (
    <>
      <div className="shadow-lg justify-center rounded-2xl p-4 bg-white dark:bg-gray-700 w-full">
        <div className="aspect-w-16 aspect-h-9 lg:aspect-none flex justify-center">
          <ReactPlayer {...videoProps} width="100%" height="100%" />
        </div>
        <div className="pt-3">
          <h3 className="mr-10 text-md truncate-2nd text-black dark:text-white antialiased sm:subpixel-antialiased md:antialiased">
            {details.title}
          </h3>
          <p className="text-sm text-gray-500">
            <a
              href={`/videolist?url=${details.channel_url}`}
              alt="channel"
              className="hover:underline hover:text-blue-500"
            >
              {details.author}
            </a>
          </p>
          <SubscribeButton channel_url={details.channel_url}/>
        </div>
      </div>
    </>
  );
};

export default VideoPlayer;
