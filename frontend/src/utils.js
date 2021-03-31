import _ from "lodash";

const BACKEND_URL = "http://localhost:8000";

const YT_API = `${BACKEND_URL}/api/youtube`;
const LBRY_API = `${BACKEND_URL}/api/lbry`;
const BITCHUTE_API = `${BACKEND_URL}/api/bitchute`;

const YOUTUBE_SEARCH = `${BACKEND_URL}/api/youtube/search/`;
const LBRY_SEARCH = `${BACKEND_URL}/api/lbry/search/`;
const BITCHUTE_SEARCH = `${BACKEND_URL}/api/bitchute/search/`;

const YOUTUBE_SEARCH_CHANNELS = `${BACKEND_URL}/api/youtube/channels`;
const LBRY_SEARCH_CHANNELS = `${BACKEND_URL}/api/lbry/channels`;

// shared
const YOUTUBE = "yt";
const LBRY = "lb";
const BITCHUTE = "bc";

export const platforms = {
  yt: "YouTube",
  lb: "Lbry",
  bc: "BitChute",
};

export const removeFromList = (myList, item) => {
  _.remove(myList, (i) => {
    return i === item;
  });
};

export const videoUrlDetails = (url) => {
  console.log(url);
  let details = [];
  if (url.includes("youtube.com")) {
    details[0] = YOUTUBE;
    details[1] = url.split("watch?v=")[1];
  } else if (url.includes("lbry.tv/@") || url.includes("odysee.com/@")) {
    details[0] = LBRY;
    details[1] = "@" + url.split("/@")[1];
  } else if (url.includes("bitchute.com/video/")) {
    details[0] = BITCHUTE;
    details[1] = _.trim(url.split("/video/")[1], "/");
  }
  details[2] = `${BACKEND_URL}/api/video/`;
  return details;
};

export const channelUrlDetails = (url) => {
  let details = [];
  if (url === "yt_popular") {
    details[0] = YOUTUBE;
    details[1] = "popular";
    details[2] = `${YT_API}/p`;
  } else if (url === "lbry_popular") {
    details[0] = LBRY;
    details[1] = "popular";
    details[2] = `${LBRY_API}/c`;
  } else if (url === "bitchute_popular") {
    details[0] = BITCHUTE;
    details[1] = "popular";
    details[2] = `${BITCHUTE_API}/c`;
  } else if (url.includes("youtube.com/")) {
    details[0] = YOUTUBE;
    details[1] = url.split("/channel/")[1];
    details[2] = `${YT_API}/c`;
  } else if (url.includes("lbry.tv/@")) {
    details[0] = LBRY;
    details[1] = url.split("lbry.tv/@")[1];
    details[2] = `${LBRY_API}/c`;
  } else if (url.includes("odysee.com/@")) {
    details[0] = LBRY;
    details[1] = url.split("odysee.com/@")[1];
    details[2] = `${LBRY_API}/c`;
  } else if (url.includes("bitchute.com/")) {
    details[0] = BITCHUTE;
    details[1] = _.trim(url.split("/channel/")[1], "/");
    details[2] = `${BITCHUTE_API}/c`;
  }
  return details;
};

const fetchVideos = async (url) => {
  let [platform, id, api_url] = channelUrlDetails(url);

  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      platform: platform,
      id: id,
    }),
  };
  const data = await fetch(api_url, requestOptions).then((response) =>
    response.json()
  );
  console.log("video list rec data:");
  console.log(data);
  if (data.ready === false) {
    console.log("failed to get videos");
    return;
  }

  return data;
};

export const fetchPopularVideos = async () => {
  const ytPromise = fetchVideos("yt_popular");
  const lbPromise = fetchVideos("lbry_popular");
  const bcPromise = fetchVideos("bitchute_popular");

  let allPopular = {};
  allPopular.platform = "all";
  allPopular.ready = false;
  allPopular.content = [];

  allPopular.content = (await ytPromise).content
    .slice(1, 10)
    .concat((await lbPromise).content.slice(1, 10))
    .concat((await bcPromise).content.slice(1, 10));

  allPopular.ready = true;
  return allPopular;
};

const fetchSearchAPi = async (search_api_url, search_query) => {
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: search_query,
      max: 15,
    }),
  };

  const data = await fetch(search_api_url, requestOptions).then((response) =>
    response.json()
  );

  return data;
};

export const fetchSearchResults = async (search_query) => {
  let allWait = [];
  allWait.push(fetchSearchAPi(YOUTUBE_SEARCH_CHANNELS, search_query));
  allWait.push(fetchSearchAPi(LBRY_SEARCH_CHANNELS, search_query));
  allWait.push(fetchSearchAPi(YOUTUBE_SEARCH, search_query));
  allWait.push(fetchSearchAPi(LBRY_SEARCH, search_query));
  allWait.push(fetchSearchAPi(BITCHUTE_SEARCH, search_query));

  let allSearch = {};
  allSearch.platform = "search";
  allSearch.ready = false;
  allSearch.content = [];

  for (const waitSub of allWait) {
    const result = await waitSub;
    if (!result || result.ready === false) {
      continue;
    }

    allSearch.content = allSearch.content.concat(result.content);
  }

  allSearch.ready = true;
  return allSearch;
};

export default fetchVideos;
