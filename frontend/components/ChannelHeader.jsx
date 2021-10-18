import React from "react";

import dynamic from "next/dynamic";
import { data } from "autoprefixer";
const SubscribeButton = dynamic(() => import("./SubscribeButton"), {
  ssr: false,
});

const ChannelHeader = ({ data }) => {
  console.log(data);
  return (
    <div>
      {/* show banner if there is one */}
      {data.channel_meta.banner ? (
        <div className="bg-cover">
          <img src={data.channel_meta.banner}></img>
        </div>
      ) : (
        ""
      )}
      <div className="-mt-1">
        <div className="container mx-auto">
          <div className="flex justify-between items-center py-4 px-16">
            <div className="flex items-center">
              {/* show number of avatar if its is available */}
              {data.channel_meta.avatar ? (
                <img
                  className="w-24 h-24 rounded-full"
                  src={data.channel_meta.avatar}
                  alt="channel_logo"
                ></img>
              ) : (
                ""
              )}
              <div className="ml-6">
                <div className="text-2xl font-normal flex items-center">
                  <span className="mr-2 text-black dark:text-white">
                    {data.channel_meta.title}
                  </span>
                </div>
                {/* show number of subscribers if the number is available */}
                {data.channel_meta.subscriberCount ? (
                  <p className="mt-2 font-hairline text-sm text-black dark:text-white">
                    {data.channel_meta.subscriberCount} subscribers
                  </p>
                ) : (
                  ""
                )}
              </div>
            </div>
            <SubscribeButton channel_url={data.channel_meta.channelUrl} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChannelHeader;
