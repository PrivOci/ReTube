import _ from "lodash";
import humanizeDuration from "humanize-duration";

const BACKEND_URL = "http://localhost:8000";

const YT_API = `${BACKEND_URL}/api/youtube`;
const LBRY_API = `${BACKEND_URL}/api/lbry`;
const BITCHUTE_API = `${BACKEND_URL}/api/bitchute`;
const RUBMLE_API = `${BACKEND_URL}/api/rumble`;

export const YOUTUBE_SEARCH = `${BACKEND_URL}/api/youtube/search/`;
export const LBRY_SEARCH = `${BACKEND_URL}/api/lbry/search/`;
export const BITCHUTE_SEARCH = `${BACKEND_URL}/api/bitchute/search/`;
export const RUMBLE_SEARCH = `${BACKEND_URL}/api/rumble/search/`;

export const YOUTUBE_SEARCH_CHANNELS = `${BACKEND_URL}/api/youtube/channels`;
export const LBRY_SEARCH_CHANNELS = `${BACKEND_URL}/api/lbry/channels`;
export const RUMBLE_SEARCH_CHANNELS = `${BACKEND_URL}/api/rumble/channels`;

const CHECK_GRAMMAR_API = `${BACKEND_URL}/api/check`;

// shared
const YOUTUBE = "yt";
const LBRY = "lb";
const BITCHUTE = "bc";
const RUBMLE = "rb";

const shortEnglishHumanizer = humanizeDuration.humanizer({
  language: "shortEn",
  languages: {
    shortEn: {
      d: () => "",
      h: () => "",
      m: () => "",
      s: () => "",
    },
  },
  delimiter: ":",
  spacer: "",
  round: true,
});

export const platforms = {
  yt: "YouTube",
  lb: "Lbry",
  bc: "BitChute",
  rb: "Rubmle",
};

export const removeFromList = (myList, item) => {
  _.remove(myList, (i) => {
    return i === item;
  });
};

export const humanizeDurationSec = (sec) => {
  const msec = sec * 1000;
  return shortEnglishHumanizer(msec);
};

/**
 * Removes "https://www" and trailing "/".
 * Used to save watched video URLs;
 * @param {string} url video url
 */
export const cleanUpUrl = (url) => {
  const lowerCaseUrl = url.toLowerCase();
  if (lowerCaseUrl.includes("youtube.com")) {
    return `yt:${_.trim(url.split("watch?v=")[1], "/")}`;
  } else if (lowerCaseUrl.includes("odysee.com/")) {
    return `lbry:${url.split("odysee.com/")[1]}`;
  } else if (lowerCaseUrl.includes("bitchute.com/video/")) {
    return `bt:${_.trim(url.split("/video/")[1], "/")}`;
  }
  return url;
};

export const videoUrlDetails = (url) => {
  url = _.trim(url, "/");
  console.log(url);
  let details = [];
  if (url.includes("youtube.com")) {
    details[0] = YOUTUBE;
    details[1] = url.split("watch?v=")[1];
  } else if (url.includes("odysee.com/")) {
    details[0] = LBRY;
    details[1] = url.split("odysee.com/")[1];
  } else if (url.includes("bitchute.com/video/")) {
    details[0] = BITCHUTE;
    details[1] = _.trim(url.split("/video/")[1], "/");
  } else if (url.includes("rumble.com/")) {
    details[0] = RUBMLE;
    details[1] = url.split("rumble.com/")[1]
  }
  details[2] = `${BACKEND_URL}/api/video/`;
  return details;
};

export const fetchDataSWR = async (url, search) => {
  if (url === "/popular") {
    return fetchPopularVideos();
  } else if (search) {
    return fetchSearchResults(decodeURI(search));
  } else {
    return fetchVideos(url);
  }
};

export const isAnonymousChannel = (channel) => {};

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
  } else if (url === "rb_popular") {
    details[0] = RUBMLE;
    details[1] = "popular";
    details[2] = `${RUBMLE_API}/c`;

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
  } else if (url.includes("rumble.com/")) {
    details[0] = RUBMLE;
    details[1] = _.trim(url.split("rumble.com/")[1], "/");
    details[2] = `${RUBMLE_API}/c`;
  }
  return details;
};

export const fetchJson = async (target_url, requestOptions) => {
  // make sure there is / at the end
  if (!target_url.endsWith("/")) {
    target_url = target_url.concat("/");
  }
  const data = await fetch(target_url, requestOptions).then((response) =>
    response.json()
  );
  return data;
};

export const fetchVideos = async (url) => {
  let [platform, id, api_url] = channelUrlDetails(url);

  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      platform: platform,
      id: id,
    }),
  };
  const data = await fetchJson(api_url, requestOptions);

  if (data.ready === false) {
    console.log(`failed to get videos: ${url}`);
    return null;
  }

  return data;
};

export const fetchPopularVideos = async () => {
  console.log("fetchPopularVideos");
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

export const fetchSearchAPi = async (search_api_url, search_query) => {
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: search_query,
      max: 15,
    }),
  };

  const data = fetchJson(search_api_url, requestOptions);

  return data;
};

const is_spell_checker_enabled = () => {
  const config = JSON.parse(localStorage.getItem("config"));
  return config["spell_checker"];
};

export const checkSentence = async (str) => {
  if (!is_spell_checker_enabled()) {
    return { need_change: false, result: "" };
  }

  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: str,
    }),
  };

  const data = fetchJson(CHECK_GRAMMAR_API, requestOptions);

  return data;
};

export const fetchSearchResults = async (search_query) => {
  console.log(`searching: ${search_query}`);
  const check_query = checkSentence(search_query);

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

  const check_result = await check_query;
  if (check_result.need_change) {
    allSearch.suggestion = check_result.result;
  }

  return allSearch;
};

export const timeSince = (timestamp) => {
  const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);

  let interval = Math.floor(seconds / 31536000);

  if (interval > 1) {
    return interval + " years";
  }

  interval = Math.floor(seconds / 2592000);
  if (interval > 1) {
    return interval + " months";
  }

  interval = Math.floor(seconds / 86400);
  if (interval > 1) {
    return interval + " days";
  }

  interval = Math.floor(seconds / 3600);
  if (interval > 1) {
    return interval + " hours";
  }

  interval = Math.floor(seconds / 60);
  if (interval > 1) {
    return interval + " minutes";
  }

  return Math.floor(seconds) + " seconds";
};
