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
 * Used to save watched video URLs;
 * @param {string} url video url
 */
export const getIdFromVideo = (url) => {
  const details = videoUrlDetails(url);
  switch (details[0]) {
    case YOUTUBE:
      return `yt:${details[1]}`;
    case LBRY:
      return `lbry:${details[1]}`;
    case BITCHUTE:
      return `bt:${details[1]}`;
    case RUBMLE:
      return `rb:${details[1]}`;
    default:
      return null;
  }
};

export const videoUrlDetails = (url) => {
  url = _.trim(url, "/");
  const parsedUrl = new URL(url);
  const href_parsed = new URL(parsedUrl.href);

  let details = [];
  if (parsedUrl.hostname.toLowerCase().includes("youtube.com")) {
    const ytId = href_parsed.searchParams.get("v");
    details[0] = YOUTUBE;
    details[1] = ytId;
  } else if (parsedUrl.hostname.toLowerCase().includes("odysee.com")) {
    const lbryId = _.trim(href_parsed.pathname, "/");
    details[0] = LBRY;
    details[1] = lbryId;
  } else if (parsedUrl.hostname.toLowerCase().includes("bitchute.com")) {
    const bcId = _.trim(href_parsed.pathname, "/video/");
    details[0] = BITCHUTE;
    details[1] = bcId;
  } else if (parsedUrl.hostname.toLowerCase().includes("rumble.com")) {
    const rbId_pre = _.trim(href_parsed.pathname, "/");
    const rbId = _.trim(rbId_pre, ".hmtl");
    details[0] = RUBMLE;
    details[1] = rbId;
  }

  return details;
};

export const fetchDataSWR = async (url, search) => {
  if (url === "/popular") {
    return fetchPopularVideos();
  } else if (search) {
    return fetchSearchResults(decodeURI(search));
  } else {
    return fetchData(url);
  }
};

export const isAnonymousChannel = (channel) => {};

export const channelUrlDetails = (url) => {
  let details = [];
  if (url === "yt_popular") {
    details[0] = YOUTUBE;
    details[1] = "popular";
    details[2] = `${YT_API}/p`;
    return details;
  } else if (url === "lbry_popular") {
    details[0] = LBRY;
    details[1] = "popular";
    details[2] = `${LBRY_API}/c`;
    return details;
  } else if (url === "bitchute_popular") {
    details[0] = BITCHUTE;
    details[1] = "popular";
    details[2] = `${BITCHUTE_API}/c`;
    return details;
  } else if (url === "rb_popular") {
    details[0] = RUBMLE;
    details[1] = "popular";
    details[2] = `${RUBMLE_API}/c`;
    return details;
  } 
  
  // TODO(me): fix this, the funciton name is misleading
  // channels
  if (url.includes("youtube.com/")) {
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

export const fetchData = async (url) => {
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
  const ytPromise = fetchData("yt_popular");
  const lbPromise = fetchData("lbry_popular");
  const bcPromise = fetchData("bitchute_popular");

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
