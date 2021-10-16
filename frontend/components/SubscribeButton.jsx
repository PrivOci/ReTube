import { conforms } from "lodash";
import React, { useState, useEffect } from "react";
import { useSnapshot } from "valtio";
import { channelUrlDetails, removeFromList } from "../utils";

import { subscriptions } from "./data";

// TODO: shared
const YOUTUBE = "yt";
const LBRY = "lb";
const BITCHUTE = "bc";
const RUMBLE = "rb";

const IsSubscribed = (subsReadOnly, channel_url) => {
  let [platform, id] = channelUrlDetails(channel_url);

  switch (platform) {
    case YOUTUBE:
      return subsReadOnly.youtube.includes(id);
    case BITCHUTE:
      return subsReadOnly.bitchute.includes(id);
    case LBRY:
      return subsReadOnly.lbry.includes(id);
    case RUMBLE:
      if ("rumble" in subsReadOnly) return subsReadOnly.rumble.includes(id);
      else return false;
    default:
      return false;
  }
};

const SubscribeButton = ({ channel_url, count }) => {
  const subsReadOnly = useSnapshot(subscriptions);
  const [isSubscribed, setIsSubscribed] = useState(false);
  useEffect(() => {
    setIsSubscribed(IsSubscribed(subsReadOnly, channel_url));

    return () => {};
  }, [subsReadOnly, channel_url]);

  return (
    <button
      className="items-center shadow bg-blue-500 mt-2 px-4 py-2 text-white hover:bg-blue-400 rounded-lg"
      onClick={() => {
        let [platform, id] = channelUrlDetails(channel_url);
        switch (platform) {
          case YOUTUBE:
            if (subsReadOnly.youtube.includes(id)) {
              removeFromList(subscriptions.youtube, id);
            } else {
              subscriptions.youtube.push(id);
            }
            break;
          case BITCHUTE:
            if (subsReadOnly.bitchute.includes(id)) {
              removeFromList(subscriptions.bitchute, id);
            } else {
              subscriptions.bitchute.push(id);
            }
            break;
          case LBRY:
            if (subsReadOnly.lbry.includes(id)) {
              removeFromList(subscriptions.lbry, id);
            } else {
              subscriptions.lbry.push(id);
            }
            break;
          case RUMBLE:
            // if existing db doesn't support rumbe
            if (subscriptions.rumble === undefined) {
              subscriptions.rumble = [];
              subscriptions.rumble.push(id);
            } else {
              if (subsReadOnly.rumble.includes(id)) {
                removeFromList(subscriptions.rumble, id);
              } else {
                subscriptions.rumble.push(id);
              }
            }
            break;

          default:
            return false;
        }
        console.log("updating subscriptions");
        localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
      }}
    >
      {isSubscribed ? `Unsubscribe [${count}]` : `Subscribe [${count}]`}
    </button>
  );
};

export default SubscribeButton;
